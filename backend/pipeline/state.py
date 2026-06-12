from typing import TypedDict, List, Dict
from models.jd import WeightedJD
from models.candidate import CandidateProfile
from models.scorecard import Scorecard

class TrueHireState(TypedDict):
    raw_jd: str
    weighted_jd: WeightedJD | None
    
    raw_cvs: List[str]
    candidates: List[CandidateProfile]
    
    llm_a_scorecards: Dict[str, Scorecard]
    llm_b_flags: Dict[str, List[str]]
    final_scorecards: List[Scorecard]
