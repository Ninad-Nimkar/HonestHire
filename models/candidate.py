from pydantic import BaseModel, Field
from typing import List, Optional

class Experience(BaseModel):
    title: str
    company: str
    duration_months: int
    description: str

class SocialSignals(BaseModel):
    linkedin_connection_count: Optional[int] = None
    linkedin_endorsements: Optional[int] = None
    x_follower_count: Optional[int] = None
    domain_relevance_score: float = 0.0

class LinkCheck(BaseModel):
    url: str
    resolves: bool = False
    identity_match: bool = False
    authenticity_score: float = 0.0
    flags: List[str] = []

class GitHubSignals(BaseModel):
    commit_count: int = 0
    commit_span_days: int = 0
    bulk_push_detected: bool = False
    ai_code_signals: List[str] = []
    real_collaboration: bool = False

class VerificationResult(BaseModel):
    links_checked: List[LinkCheck] = []
    github_signals: Optional[GitHubSignals] = None
    overall_authenticity: float = 0.0

class InferredSkill(BaseModel):
    name: str
    source_skill: str
    confidence: float

class CandidateProfile(BaseModel):
    id: str
    raw_cv: str
    name: str
    email: str
    linkedin_url: str = ""
    github_url: str = ""
    other_links: List[str] = []
    skills_claimed: List[str] = []
    experience: List[Experience] = []
    social_signals: Optional[SocialSignals] = None
    verification: Optional[VerificationResult] = None
    inferred_skills: List[InferredSkill] = []
