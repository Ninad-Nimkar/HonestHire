"""
Node 12: Ranker — final ranking, blocker filtering, CSV + JSON output.
"""

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

from config import settings
from models.scorecard import Scorecard
from models.jd import WeightedJD, SkillTier
from models.candidate import CandidateProfile


async def ranker_node(state: dict) -> dict:
    """Rank candidates, filter blockers, write output files."""
    scorecards = state.get("scorecards", [])
    candidates = state.get("candidates", [])
    weighted_jd = state.get("weighted_jd")

    # Build candidate skill lookup
    candidate_skills = {}
    for c in candidates:
        if isinstance(c, dict):
            c = CandidateProfile(**c)
        candidate_skills[c.id] = set(s.lower() for s in c.skills_claimed)

    # Get blocker skills
    blocker_skills = set()
    if weighted_jd:
        jd = weighted_jd if isinstance(weighted_jd, WeightedJD) else WeightedJD(**weighted_jd)
        for skill in jd.skills:
            if skill.tier == SkillTier.blocker:
                blocker_skills.add(skill.name.lower())
                for alias in skill.aliases:
                    blocker_skills.add(alias.lower())

    # Process scorecards
    ranked = []
    for sc in scorecards:
        if isinstance(sc, dict):
            sc = Scorecard(**sc)

        # Check blocker skills
        if blocker_skills:
            cand_skills = candidate_skills.get(sc.candidate_id, set())
            missing_blockers = blocker_skills - cand_skills

            # Allow if candidate has at least some blocker skills
            if missing_blockers and len(missing_blockers) == len(blocker_skills):
                sc.excluded = True
                sc.exclusion_reason = f"Missing all blocker skills: {', '.join(missing_blockers)}"

        ranked.append(sc)

    # Sort non-excluded by weighted_total
    included = [s for s in ranked if not s.excluded]
    excluded = [s for s in ranked if s.excluded]

    included.sort(key=lambda s: s.weighted_total, reverse=True)

    # Assign ranks
    for rank, sc in enumerate(included, 1):
        sc.final_rank = rank

    for sc in excluded:
        sc.final_rank = 0

    final_scorecards = included + excluded

    # Write output files
    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    scorecards_dir = output_dir / "scorecards"
    scorecards_dir.mkdir(exist_ok=True)

    # Write CSV
    csv_path = output_dir / "ranked_candidates.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank", "Candidate ID", "Name", "Weighted Total",
            "Skills Fit", "Experience Relevance", "Behavioral Signals",
            "Trajectory", "Social Credibility", "AI Risk Score",
            "Confidence", "Challenger Flags", "Excluded", "Exclusion Reason",
        ])
        for sc in final_scorecards:
            writer.writerow([
                sc.final_rank, sc.candidate_id, sc.candidate_name,
                f"{sc.weighted_total:.3f}",
                f"{sc.scores.skills_fit:.2f}",
                f"{sc.scores.experience_relevance:.2f}",
                f"{sc.scores.behavioral_signals:.2f}",
                f"{sc.scores.trajectory:.2f}",
                f"{sc.scores.social_credibility:.2f}",
                f"{sc.ai_risk_score:.2f}",
                sc.confidence.value,
                "; ".join(sc.challenger_flags),
                sc.excluded,
                sc.exclusion_reason,
            ])

    # Write individual scorecard JSONs
    for sc in final_scorecards:
        sc_path = scorecards_dir / f"{sc.candidate_id}.json"
        with open(sc_path, "w") as f:
            json.dump(sc.model_dump(), f, indent=2, default=str)

    return {
        "current_node": "ranker",
        "scorecards": final_scorecards,
    }
