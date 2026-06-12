import os
import uuid
from langchain_openai import ChatOpenAI
from pipeline.state import TrueHireState
from models.candidate import CandidateProfile

def profile_parser_node(state: TrueHireState) -> TrueHireState:
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"), 
        temperature=0, 
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    structured_llm = llm.with_structured_output(CandidateProfile)
    
    candidates = []
    for cv in state.get("raw_cvs", []):
        prompt = f"Extract structured candidate information from the following CV. Fill all fields appropriately.\n\n{cv}"
        try:
            profile = structured_llm.invoke(prompt)
            profile.id = str(uuid.uuid4())
            profile.raw_cv = cv
            candidates.append(profile)
        except Exception as e:
            print("Error parsing profile:", e)
            
    state["candidates"] = candidates
    return state
