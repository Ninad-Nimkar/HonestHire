import os
from langchain_anthropic import ChatAnthropic
from pipeline.state import TrueHireState
from models.jd import WeightedJD, Skill, Tier
from pydantic import BaseModel, Field

class ExtractedSkills(BaseModel):
    skills: list[str] = Field(description="List of skills extracted from the job description")

def jd_parser_node(state: TrueHireState) -> TrueHireState:
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620", 
        temperature=0, 
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    
    # Extract raw skills list using structured output
    structured_llm = llm.with_structured_output(ExtractedSkills)
    prompt = f"Extract all the required and preferred technical skills, tools, and soft skills from this job description:\n\n{state['raw_jd']}"
    
    result = structured_llm.invoke(prompt)
    
    skills = []
    for s in result.skills:
        skills.append(Skill(
            name=s,
            tier=Tier.nice_to_have, # default
            weight=0.2, # default
            aliases=[]
        ))
        
    weighted_jd = WeightedJD(
        raw_text=state["raw_jd"],
        skills=skills
    )
    
    state["weighted_jd"] = weighted_jd
    return state
