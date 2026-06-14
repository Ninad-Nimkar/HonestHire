"""
Node 9: LLM Analyst — GPT-4o "senior recruiter" scores each candidate on 5 axes.
"""

import json
from langchain_openai import ChatOpenAI
from config import settings
from models.candidate import CandidateProfile
from models.scorecard import Scorecard, ScoreAxes, ConfidenceLevel
from models.jd import WeightedJD

ANALYST_SYSTEM_PROMPT = """You are a senior technical recruiter with 15 years experience.
Given a verified candidate profile and weighted job description, score 
the candidate on 5 axes: skills_fit, experience_relevance, 
behavioral_signals, trajectory, social_credibility. Each score 0–1.
Be thorough but fair. Base scores only on verified signals, not claims.
Output JSON matching this schema:
{
  "scores": {
    "skills_fit": 0.0,
    "experience_relevance": 0.0,
    "behavioral_signals": 0.0,
    "trajectory": 0.0,
    "social_credibility": 0.0
  },
  "reasoning": "detailed explanation of scoring decisions"
}"""


async def llm_analyst_node(state: dict) -> dict:
    """Score each candidate using LLM-A (analyst persona)."""
    candidates = state.get("candidates", [])
    weighted_jd = state.get("weighted_jd")

    if not settings.OPENAI_API_KEY:
        # Return placeholder scorecards without LLM
        scorecards = [_placeholder_scorecard(c) for c in candidates]
        return {"current_node": "llm_analyst", "scorecards": scorecards}

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.3,
    )

    scorecards = []
    for candidate in candidates:
        if isinstance(candidate, dict):
            candidate = CandidateProfile(**candidate)

        try:
            scorecard = await _score_candidate(llm, candidate, weighted_jd)
            scorecards.append(scorecard)
        except Exception as e:
            scorecards.append(_placeholder_scorecard(candidate))

    return {"current_node": "llm_analyst", "scorecards": scorecards}


async def _score_candidate(
    llm: ChatOpenAI, candidate: CandidateProfile, jd: WeightedJD | None
) -> Scorecard:
    """Use LLM to score a single candidate."""
    jd_text = jd.raw_text[:2000] if jd else "No JD provided"
    jd_skills = ", ".join(s.name for s in (jd.skills if jd else []))

    candidate_summary = f"""
Name: {candidate.name}
Skills Claimed: {', '.join(candidate.skills_claimed)}
Experience: {len(candidate.experience)} roles
GitHub: {candidate.verification.github_signals.commit_count} commits, {candidate.verification.github_signals.public_repos} repos
Collaboration: {candidate.verification.github_signals.real_collaboration}
Bulk Push: {candidate.verification.github_signals.bulk_push_detected}
Links Valid: {sum(1 for l in candidate.verification.links_checked if l.resolves)}/{len(candidate.verification.links_checked)}
AI Risk Score: {candidate.ai_risk_score}
AI Flags: {', '.join(candidate.ai_risk_flags) if candidate.ai_risk_flags else 'None'}
Inferred Skills: {', '.join(f'{s.name} ({s.confidence:.0%})' for s in candidate.inferred_skills[:5])}
Social: LinkedIn accessible={candidate.social_signals.linkedin_accessible}, Cross-ref={candidate.social_signals.cross_reference_match}
"""

    prompt = f"""Job Description Skills: {jd_skills}

Candidate Profile:
{candidate_summary}

Score this candidate on all 5 axes (0-1 each). Base scores on verified signals only."""

    response = await llm.ainvoke([
        {"role": "system", "content": ANALYST_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    content = response.content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    data = json.loads(content)
    scores_data = data.get("scores", {})

    return Scorecard(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        scores=ScoreAxes(
            skills_fit=float(scores_data.get("skills_fit", 0.5)),
            experience_relevance=float(scores_data.get("experience_relevance", 0.5)),
            behavioral_signals=float(scores_data.get("behavioral_signals", 0.5)),
            trajectory=float(scores_data.get("trajectory", 0.5)),
            social_credibility=float(scores_data.get("social_credibility", 0.5)),
        ),
        analyst_reasoning=data.get("reasoning", ""),
        ai_risk_score=candidate.ai_risk_score,
    )


def _placeholder_scorecard(candidate) -> Scorecard:
    """Generate a placeholder scorecard when LLM is unavailable."""
    if isinstance(candidate, dict):
        candidate = CandidateProfile(**candidate)

    return Scorecard(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        scores=ScoreAxes(
            skills_fit=0.5,
            experience_relevance=0.5,
            behavioral_signals=0.5,
            trajectory=0.5,
            social_credibility=0.5,
        ),
        analyst_reasoning="LLM analysis unavailable — placeholder scores generated.",
        ai_risk_score=candidate.ai_risk_score,
    )
