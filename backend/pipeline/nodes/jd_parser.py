import os
from langchain_openai import ChatOpenAI
from pipeline.state import TrueHireState
from models.jd import WeightedJD, Skill, Tier
from pydantic import BaseModel, Field

class ExtractedSkills(BaseModel):
    skills: list[str] = Field(description="List of skills extracted from the job description")

def jd_parser_node(state: TrueHireState) -> TrueHireState:
    if state.get("weighted_jd") is not None:
        # Already parsed by frontend HR gate
        return state
        
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"), 
        temperature=0, 
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    structured_llm = llm.with_structured_output(ExtractedSkills)
    prompt = f"Extract all the required and preferred technical skills, tools, and soft skills from this job description:\n\n{state['raw_jd']}"
    
    try:
        result = structured_llm.invoke(prompt)
        skills = []
        for s in result.skills:
            skills.append(Skill(
                name=s,
                tier=Tier.nice_to_have,
                weight=0.2,
                aliases=[]
            ))
            
        state["weighted_jd"] = WeightedJD(
            raw_text=state["raw_jd"],
            skills=skills
        )
    except Exception:
        pass
        
    return state
