import os
from langchain_openai import ChatOpenAI
from pipeline.state import TrueHireState
from pydantic import BaseModel, Field

class AIDetectionResult(BaseModel):
    risk_score: float = Field(description="0.0 to 1.0 indicating likelihood of AI generation")
    flags: list[str] = Field(description="Specific AI signals found")

def ai_detector_node(state: TrueHireState) -> TrueHireState:
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"), 
        temperature=0, 
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    structured_llm = llm.with_structured_output(AIDetectionResult)
    
    candidates = state.get("candidates", [])
    for cand in candidates:
        prompt = f"Analyze this candidate's written content for AI generation signals: no personal voice, suspiciously complete coverage, zero typos across large body of work, no opinions or hedging.\n\nContent:\n{cand.raw_cv}"
        
        try:
            res = structured_llm.invoke(prompt)
            if cand.verification:
                cand.verification.overall_authenticity = max(0.0, 1.0 - res.risk_score)
                if cand.verification.links_checked:
                    cand.verification.links_checked[0].flags.extend(res.flags)
        except Exception:
            pass
            
    return state
