from typing import TypedDict, List, Dict
from models.jd import WeightedJD
from models.candidate import CandidateProfile
from models.scorecard import Scorecard

class TrueHireState(TypedDict):
    # Job Description Phase
    raw_jd: str
    weighted_jd: WeightedJD | None
    
    # Candidate Processing Phase (can process multiple)
    raw_cvs: List[str] # incoming raw CVs
    candidates: List[CandidateProfile]
    
    # Scorecards (generated per candidate)
    llm_a_scorecards: Dict[str, Scorecard]
    llm_b_flags: Dict[str, List[str]]
    final_scorecards: List[Scorecard]
