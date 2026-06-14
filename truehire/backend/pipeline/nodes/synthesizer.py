"""
Node 11: Synthesizer — merges LLM-A and LLM-B outputs, applies flag penalties.
"""

from config import settings
from models.scorecard import Scorecard, ConfidenceLevel
from models.jd import WeightedJD


async def synthesizer_node(state: dict) -> dict:
    """Merge analyst and challenger outputs, compute weighted totals."""
    scorecards = state.get("scorecards", [])
    weighted_jd = state.get("weighted_jd")
    threshold = settings.DEBATE_DISAGREEMENT_THRESHOLD

    synthesized = []
    for scorecard in scorecards:
        if isinstance(scorecard, dict):
            scorecard = Scorecard(**scorecard)

        # Apply challenger flag penalties
        flag_count = len(scorecard.challenger_flags)
        penalty = min(flag_count * 0.05, 0.2)  # Max -0.2 penalty

        # Compute weighted total from score axes
        scores = scorecard.scores
        raw_scores = [
            scores.skills_fit,
            scores.experience_relevance,
            scores.behavioral_signals,
            scores.trajectory,
            scores.social_credibility,
        ]
        avg_score = sum(raw_scores) / len(raw_scores) if raw_scores else 0.5

        # Apply JD skill weights if available
        if weighted_jd and weighted_jd.skills:
            weighted_total = _compute_jd_weighted_score(scores, weighted_jd)
        else:
            weighted_total = avg_score

        # Apply challenger penalty
        weighted_total = max(0.0, weighted_total - penalty)
        scorecard.weighted_total = round(weighted_total, 3)

        # Determine confidence level
        if flag_count == 0 and scorecard.ai_risk_score < 0.3:
            scorecard.confidence = ConfidenceLevel.high
        elif flag_count >= 3 or scorecard.ai_risk_score >= 0.7:
            scorecard.confidence = ConfidenceLevel.needs_review
        elif flag_count >= 1 or scorecard.ai_risk_score >= 0.4:
            scorecard.confidence = ConfidenceLevel.medium
        else:
            scorecard.confidence = ConfidenceLevel.high

        # AI risk override
        if scorecard.ai_risk_score >= settings.AI_RISK_THRESHOLD:
            scorecard.confidence = ConfidenceLevel.needs_review

        synthesized.append(scorecard)

    return {"current_node": "synthesizer", "scorecards": synthesized}


def _compute_jd_weighted_score(scores, jd: WeightedJD) -> float:
    """Compute a score weighted by JD skill priorities."""
    # Skills fit gets extra weight for blocker-heavy JDs
    blocker_count = sum(1 for s in jd.skills if s.tier.value == "blocker")
    total_skills = len(jd.skills) or 1
    blocker_ratio = blocker_count / total_skills

    weights = {
        "skills_fit": 0.30 + (blocker_ratio * 0.10),  # 30-40%
        "experience_relevance": 0.25,
        "behavioral_signals": 0.15,
        "trajectory": 0.15,
        "social_credibility": 0.15 - (blocker_ratio * 0.10),  # 5-15%
    }

    # Normalize weights
    total_weight = sum(weights.values())
    weighted = (
        scores.skills_fit * weights["skills_fit"] / total_weight
        + scores.experience_relevance * weights["experience_relevance"] / total_weight
        + scores.behavioral_signals * weights["behavioral_signals"] / total_weight
        + scores.trajectory * weights["trajectory"] / total_weight
        + scores.social_credibility * weights["social_credibility"] / total_weight
    )

    return weighted
