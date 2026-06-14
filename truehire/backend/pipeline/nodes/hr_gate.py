"""
Node 2: HR Gate — builds WeightedJD from HR tier decisions.
Flags inflated/vague requirements automatically.
"""

import re
from models.jd import Skill, SkillTier, WeightedJD
from config import settings


# Known vague buzzwords
VAGUE_TERMS = {"rockstar", "ninja", "wizard", "guru", "unicorn", "10x", "superstar"}

# Technologies with known release dates (approx years since creation)
TECH_AGES: dict[str, int] = {
    "kubernetes": 10, "k8s": 10,
    "docker": 12, "react": 11, "vue": 10,
    "go": 14, "golang": 14, "rust": 14,
    "tensorflow": 10, "pytorch": 9,
    "nextjs": 8, "next.js": 8,
    "fastapi": 6, "langchain": 3,
    "langgraph": 2, "svelte": 8,
}


def _flag_inflated_requirements(skill: Skill, raw_text: str) -> str | None:
    """Check if a skill requirement is inflated and return reason."""
    name_lower = skill.name.lower()

    # Check vague terms
    if name_lower in VAGUE_TERMS:
        return f'Vague requirement — "{skill.name}" should be rewritten as specific competencies'

    # Check for vague terms in skill name
    for term in VAGUE_TERMS:
        if term in name_lower:
            return f'Contains vague term "{term}" — consider rewriting to specific skills'

    # Check if years required > technology age
    # Search for patterns like "8+ years of Kubernetes" or "10 years experience in Docker"
    patterns = [
        rf"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?{re.escape(name_lower)}",
        rf"{re.escape(name_lower)}.*?(\d+)\+?\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, raw_text.lower())
        if match:
            years_required = int(match.group(1))
            tech_age = TECH_AGES.get(name_lower)
            if tech_age and years_required > tech_age:
                return (f"Requires {years_required}+ years experience with a "
                        f"~{tech_age}-year-old technology")

    return None


async def hr_gate_node(state: dict) -> dict:
    """
    Build WeightedJD from HR tier decisions.
    If no HR decisions yet, use extracted skills with auto-flagging.
    """
    raw_text = state.get("raw_jd_text", "")
    extracted_skills = state.get("extracted_skills", [])
    tier_weights = settings.SCORE_WEIGHTS

    # Apply weights and check for inflated requirements
    weighted_skills = []
    for skill in extracted_skills:
        # Ensure skill is a Skill object
        if isinstance(skill, dict):
            skill = Skill(**skill)

        # Auto-flag inflated requirements
        flag = _flag_inflated_requirements(skill, raw_text)
        if flag and not skill.flagged_reason:
            skill.flagged_reason = flag

        # Apply weight based on tier
        skill.weight = tier_weights.get(skill.tier.value, 0.7)
        weighted_skills.append(skill)

    weighted_jd = WeightedJD(
        raw_text=raw_text,
        title=state.get("job_title", ""),
        skills=weighted_skills,
    )

    return {
        "current_node": "hr_gate",
        "weighted_jd": weighted_jd,
        "hr_decisions_received": True,
    }
