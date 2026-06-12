import os
from langchain_anthropic import ChatAnthropic
from pipeline.state import TrueHireState
from models.scorecard import Scorecard, Scores, ConfidenceLevel

def llm_analyst_node(state: TrueHireState) -> TrueHireState:
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620", 
        temperature=0, 
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    structured_llm = llm.with_structured_output(Scorecard)
    
    jd = state.get("weighted_jd")
    jd_text = jd.model_dump_json() if jd else ""
    
    scorecards = {}
    candidates = state.get("candidates", [])
    
    for cand in candidates:
        prompt = f"""You are a senior technical recruiter. 
Given a verified candidate profile and weighted job description, score the candidate on 5 axes (skills_fit, experience_relevance, behavioral_signals, trajectory, social_credibility) from 0.0 to 1.0.
Be generous but accurate. Use only verified signals, not claims.

Candidate ID: {cand.id}
Profile: {cand.model_dump_json()}
Job Description: {jd_text}
"""
        try:
            scorecard = structured_llm.invoke(prompt)
            scorecard.candidate_id = cand.id
            scorecards[cand.id] = scorecard
        except Exception:
            # Fallback
            scorecards[cand.id] = Scorecard(
                candidate_id=cand.id,
                scores=Scores(),
                weighted_total=0.0,
                analyst_reasoning="Failed to generate.",
                challenger_flags=[],
                confidence=ConfidenceLevel.needs_review,
                final_rank=0
            )
            
    state["llm_a_scorecards"] = scorecards
    return state
