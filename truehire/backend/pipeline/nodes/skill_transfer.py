"""
Node 8: Skill Transfer — infers adjacent skills from claimed skills using skill graph.
"""

import json
from pathlib import Path
from models.candidate import CandidateProfile, InferredSkill
from config import settings


# Load skill graph at module level
_skill_graph: dict = {}


def _load_skill_graph() -> dict:
    """Load skill graph from JSON file."""
    global _skill_graph
    if _skill_graph:
        return _skill_graph

    graph_path = Path(settings.DATA_DIR) / "skill_graph.json"
    if graph_path.exists():
        with open(graph_path, "r") as f:
            _skill_graph = json.load(f)
    return _skill_graph


async def skill_transfer_node(state: dict) -> dict:
    """Infer adjacent skills for each candidate based on skill graph."""
    candidates = state.get("candidates", [])
    graph = _load_skill_graph()
    multipliers = settings.INFERRED_SKILL_MULTIPLIER
    analyzed = []

    for candidate in candidates:
        if isinstance(candidate, dict):
            candidate = CandidateProfile(**candidate)

        inferred = []
        claimed_lower = {s.lower() for s in candidate.skills_claimed}

        for claimed_skill in candidate.skills_claimed:
            skill_key = claimed_skill.lower()

            if skill_key not in graph:
                continue

            skill_data = graph[skill_key]

            # Direct transfers (highest confidence)
            for transfer in skill_data.get("direct_transfers", []):
                t_name = transfer["skill"]
                if t_name.lower() not in claimed_lower:
                    confidence = transfer.get("confidence", multipliers["direct"])
                    # Cross-check with social signals
                    confidence = _adjust_confidence(candidate, t_name, confidence)

                    inferred.append(InferredSkill(
                        name=t_name,
                        source_skill=claimed_skill,
                        confidence=round(confidence, 2),
                        transfer_type="direct",
                    ))

            # Adjacent transfers (medium confidence)
            for transfer in skill_data.get("adjacent_transfers", []):
                t_name = transfer["skill"]
                if t_name.lower() not in claimed_lower:
                    confidence = transfer.get("confidence", multipliers["adjacent"])
                    confidence = _adjust_confidence(candidate, t_name, confidence)

                    inferred.append(InferredSkill(
                        name=t_name,
                        source_skill=claimed_skill,
                        confidence=round(confidence, 2),
                        transfer_type="adjacent",
                    ))

        # Deduplicate: keep highest confidence per skill
        seen = {}
        for inf in inferred:
            key = inf.name.lower()
            if key not in seen or inf.confidence > seen[key].confidence:
                seen[key] = inf

        candidate.inferred_skills = list(seen.values())
        analyzed.append(candidate)

    return {"current_node": "skill_transfer", "candidates": analyzed}


def _adjust_confidence(
    candidate: CandidateProfile, inferred_skill: str, base_confidence: float
) -> float:
    """Adjust inferred skill confidence based on supporting evidence."""
    # Check GitHub languages
    github_langs = {l.lower() for l in candidate.verification.github_signals.top_languages}
    if inferred_skill.lower() in github_langs:
        return min(1.0, base_confidence * 1.15)  # Boost if found in GitHub

    # Check if there's zero evidence of the inferred skill
    social_notes = " ".join(candidate.social_signals.notes).lower()
    if inferred_skill.lower() in social_notes:
        return min(1.0, base_confidence * 1.1)

    # Penalize if no evidence at all
    if candidate.verification.github_signals.commit_count > 0 and not github_langs:
        return base_confidence * 0.8

    return base_confidence
