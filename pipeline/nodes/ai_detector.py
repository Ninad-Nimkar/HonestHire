import os
from langchain_anthropic import ChatAnthropic
from pipeline.state import TrueHireState
from pydantic import BaseModel, Field

class AIDetectionResult(BaseModel):
    risk_score: float = Field(description="0.0 to 1.0 indicating likelihood of AI generation")
    flags: list[str] = Field(description="Specific AI signals found")

def ai_detector_node(state: TrueHireState) -> TrueHireState:
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620", 
        temperature=0, 
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    structured_llm = llm.with_structured_output(AIDetectionResult)
    
    candidates = state.get("candidates", [])
    for cand in candidates:
        prompt = f"Analyze this candidate's written content for AI generation signals: no personal voice, suspiciously complete coverage, zero typos across large body of work, no opinions or hedging.\n\nContent:\n{cand.raw_cv}"
        
        try:
            res = structured_llm.invoke(prompt)
            if cand.verification:
                # Store AI risk as inverse of overall authenticity
                cand.verification.overall_authenticity = max(0.0, 1.0 - res.risk_score)
                cand.verification.links_checked[0].flags.extend(res.flags) if cand.verification.links_checked else None
        except Exception:
            pass
            
    return state
