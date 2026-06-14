"""
Candidate profile models — full data model for a job candidate.

Follows pydantic-models-py skill: typed, validated, documented.
"""

from pydantic import BaseModel, Field


class Experience(BaseModel):
    """A single work experience entry."""
    title: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""


class LinkCheck(BaseModel):
    """Result of verifying a single URL from a candidate's profile."""
    url: str
    resolves: bool = False
    identity_match: bool = False
    authenticity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    flags: list[str] = Field(default_factory=list)


class GitHubSignals(BaseModel):
    """Signals extracted from a candidate's GitHub profile."""
    username: str = ""
    commit_count: int = 0
    commit_span_days: int = 0
    bulk_push_detected: bool = False
    ai_code_signals: list[str] = Field(default_factory=list)
    real_collaboration: bool = False
    top_languages: list[str] = Field(default_factory=list)
    public_repos: int = 0


class SocialSignals(BaseModel):
    """Signals from social media / online presence."""
    linkedin_accessible: bool = False
    linkedin_connection_count: int | None = None
    linkedin_endorsement_ratio: float | None = None
    linkedin_post_recency: str | None = None
    twitter_accessible: bool = False
    twitter_domain_relevance: float = 0.0
    twitter_account_age_days: int | None = None
    cross_reference_match: bool = False
    notes: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    """Combined verification results for a candidate."""
    links_checked: list[LinkCheck] = Field(default_factory=list)
    github_signals: GitHubSignals = Field(default_factory=GitHubSignals)
    social_signals: SocialSignals = Field(default_factory=SocialSignals)
    overall_authenticity: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Overall authenticity score 0–1",
    )


class InferredSkill(BaseModel):
    """A skill inferred from an adjacent claimed skill."""
    name: str
    source_skill: str = Field(..., description="The claimed skill this was inferred from")
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Inference confidence: direct=0.85, adjacent=0.65, stretch=0.4",
    )
    transfer_type: str = Field(
        default="adjacent",
        description="Type of skill transfer: direct, adjacent, or stretch",
    )


class CandidateProfile(BaseModel):
    """Full candidate profile — the core data object flowing through the pipeline."""
    id: str
    name: str = ""
    email: str = ""
    raw_cv: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    other_links: list[str] = Field(default_factory=list)
    skills_claimed: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    social_signals: SocialSignals = Field(default_factory=SocialSignals)
    verification: VerificationResult = Field(default_factory=VerificationResult)
    inferred_skills: list[InferredSkill] = Field(default_factory=list)
    ai_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ai_risk_flags: list[str] = Field(default_factory=list)


class CandidateUploadResponse(BaseModel):
    """Response from candidate upload."""
    count: int
    candidates: list[CandidateProfile]
