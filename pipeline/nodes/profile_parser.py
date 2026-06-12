import os
import uuid
from langchain_anthropic import ChatAnthropic
from pipeline.state import TrueHireState
from models.candidate import CandidateProfile

def profile_parser_node(state: TrueHireState) -> TrueHireState:
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620", 
        temperature=0, 
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    structured_llm = llm.with_structured_output(CandidateProfile)
    
    candidates = []
    for cv in state.get("raw_cvs", []):
        prompt = f"Extract structured candidate information from the following CV. Fill all fields appropriately.\n\n{cv}"
        profile = structured_llm.invoke(prompt)
        profile.id = str(uuid.uuid4())
        profile.raw_cv = cv
        candidates.append(profile)
        
    state["candidates"] = candidates
    return state
