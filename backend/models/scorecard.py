from pydantic import BaseModel
from enum import Enum
from typing import List

class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    needs_review = "needs_review"

class Scores(BaseModel):
    skills_fit: float = 0.0
    experience_relevance: float = 0.0
    behavioral_signals: float = 0.0
    trajectory: float = 0.0
    social_credibility: float = 0.0

class Scorecard(BaseModel):
    candidate_id: str
    scores: Scores
    weighted_total: float = 0.0
    analyst_reasoning: str = ""
    challenger_flags: List[str] = []
    confidence: ConfidenceLevel = ConfidenceLevel.needs_review
    ai_risk_score: float = 0.0
    final_rank: int = 0
