import os
from langchain_openai import ChatOpenAI
from pipeline.state import TrueHireState
from pydantic import BaseModel, Field

class ChallengerOutput(BaseModel):
    flags: list[str] = Field(description="Weak reasoning, unverified claims treated as facts, title inflation, etc.")

def llm_challenger_node(state: TrueHireState) -> TrueHireState:
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"), 
        temperature=0, 
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    structured_llm = llm.with_structured_output(ChallengerOutput)
    
    scorecards = state.get("llm_a_scorecards", {})
    candidates = {c.id: c for c in state.get("candidates", [])}
    
    llm_b_flags = {}
    
    for cid, scorecard in scorecards.items():
        cand = candidates.get(cid)
        if not cand:
            continue
            
        prompt = f"""You are a skeptical hiring manager reviewing a recruiter's candidate scorecard.
Your job is to find: weak reasoning, unverified claims treated as facts, title inflation, scores inconsistent with evidence, missing red flags. Be specific and cite evidence.

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
