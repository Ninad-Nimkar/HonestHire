"""
Node 10: LLM Challenger — GPT-4o "skeptical hiring manager" challenges analyst scores.
"""

import json
from langchain_openai import ChatOpenAI
from config import settings
from models.candidate import CandidateProfile
from models.scorecard import Scorecard

CHALLENGER_SYSTEM_PROMPT = """You are a skeptical hiring manager reviewing a recruiter's 
candidate scorecard. Your job is to find: weak reasoning, unverified 
claims treated as facts, title inflation, scores inconsistent with 
evidence, missing red flags. Be specific and cite evidence.
Output valid JSON:
{
  "flags": ["specific flag 1", "specific flag 2"],
  "score_adjustments": {
    "skills_fit": -0.05,
    "experience_relevance": 0.0,
    "behavioral_signals": -0.1,
    "trajectory": 0.0,
    "social_credibility": -0.05
  }
}"""


async def llm_challenger_node(state: dict) -> dict:
    """Challenge each candidate's scorecard using LLM-B (skeptical persona)."""
    scorecards = state.get("scorecards", [])
    candidates = state.get("candidates", [])

    if not settings.OPENAI_API_KEY:
        # Return scorecards unchanged
        return {"current_node": "llm_challenger", "scorecards": scorecards}

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.4,
    )

    # Build candidate lookup
    candidate_map = {}
    for c in candidates:
        if isinstance(c, dict):
            c = CandidateProfile(**c)
        candidate_map[c.id] = c

    challenged = []
    for scorecard in scorecards:
        if isinstance(scorecard, dict):
            scorecard = Scorecard(**scorecard)

        candidate = candidate_map.get(scorecard.candidate_id)
        if candidate:
            try:
                scorecard = await _challenge_scorecard(llm, scorecard, candidate)
            except Exception:
                pass

        challenged.append(scorecard)

    return {"current_node": "llm_challenger", "scorecards": challenged}


async def _challenge_scorecard(
    llm: ChatOpenAI, scorecard: Scorecard, candidate: CandidateProfile
) -> Scorecard:
    """Challenge a single scorecard with LLM-B."""
    prompt = f"""Review this recruiter's scorecard for candidate "{candidate.name}":

Scores:
- Skills Fit: {scorecard.scores.skills_fit}
- Experience Relevance: {scorecard.scores.experience_relevance}
- Behavioral Signals: {scorecard.scores.behavioral_signals}
- Trajectory: {scorecard.scores.trajectory}
- Social Credibility: {scorecard.scores.social_credibility}

Analyst Reasoning: {scorecard.analyst_reasoning}

Candidate Facts:
- Skills Claimed: {', '.join(candidate.skills_claimed)}
- AI Risk Score: {candidate.ai_risk_score}
- AI Flags: {', '.join(candidate.ai_risk_flags) if candidate.ai_risk_flags else 'None'}
- GitHub Commits: {candidate.verification.github_signals.commit_count}
- Bulk Push: {candidate.verification.github_signals.bulk_push_detected}
- Links Valid: {sum(1 for l in candidate.verification.links_checked if l.resolves)}/{len(candidate.verification.links_checked)}
- LinkedIn Accessible: {candidate.social_signals.linkedin_accessible}

Find weak reasoning, unverified claims, title inflation, missing red flags."""

    response = await llm.ainvoke([
        {"role": "system", "content": CHALLENGER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    content = response.content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    data = json.loads(content)
    scorecard.challenger_flags = data.get("flags", [])

    return scorecard
