import os
from langchain_anthropic import ChatAnthropic
from pipeline.state import TrueHireState
from pydantic import BaseModel, Field

class ChallengerOutput(BaseModel):
    flags: list[str] = Field(description="Weak reasoning, unverified claims treated as facts, title inflation, etc.")

def llm_challenger_node(state: TrueHireState) -> TrueHireState:
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620", 
        temperature=0, 
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    structured_llm = llm.with_structured_output(ChallengerOutput)
    
    scorecards = state.get("llm_a_scorecards", {})
    candidates = {c.id: c for c in state.get("candidates", [])}
    
    llm_b_flags = {}
    
    for cid, scorecard in scorecards.items():
        cand = candidates.get(cid)
        if not cand:
            continue
            
        prompt = f"""You are a skeptical hiring manager reviewing a recruiter's scorecard.
Find weak reasoning, unverified claims treated as facts, title inflation, and scores that don't match the evidence. Be specific.

Candidate Profile: {cand.model_dump_json()}
Recruiter Scorecard: {scorecard.model_dump_json()}
"""
        try:
            res = structured_llm.invoke(prompt)
            llm_b_flags[cid] = res.flags
        except Exception:
            llm_b_flags[cid] = []
            
    state["llm_b_flags"] = llm_b_flags
    return state
