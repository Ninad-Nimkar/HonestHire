"""
Job Description models — Pydantic V2 with multi-model pattern.

Follows pydantic-models-py skill: Base/Create/Response separation.
"""

from enum import Enum
from pydantic import BaseModel, Field


class SkillTier(str, Enum):
    """Priority tier for a skill requirement."""
    blocker = "blocker"
    important = "important"
    nice_to_have = "nice_to_have"


class Skill(BaseModel):
    """A single skill extracted from a job description."""
    name: str = Field(..., description="Skill name, e.g. 'Python'")
    tier: SkillTier = Field(
        default=SkillTier.important,
        description="Priority tier assigned by HR",
    )
    weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Numeric weight: blocker=1.0, important=0.7, nice_to_have=0.2",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description="Related terms the LLM infers, e.g. ['Python3', 'CPython']",
    )
    flagged_reason: str | None = Field(
        default=None,
        description="Why this skill was flagged as potentially inflated",
    )


class WeightedJD(BaseModel):
    """A fully weighted job description ready for pipeline processing."""
    raw_text: str = Field(..., description="Original JD text")
    title: str = Field(default="", description="Extracted job title")
    skills: list[Skill] = Field(default_factory=list)


# --- API Request/Response models ---

class JDUploadRequest(BaseModel):
    """Request body for POST /api/jd/upload."""
    raw_text: str = Field(..., min_length=10, description="Raw JD text to parse")


class JDUploadResponse(BaseModel):
    """Response from JD upload — extracted skills for HR review."""
    title: str
    skills: list[Skill]
    flagged_count: int = Field(
        default=0,
        description="Number of skills flagged as potentially inflated",
    )


class SkillPriority(BaseModel):
    """A single skill with HR-assigned tier."""
    name: str
    tier: SkillTier


class JDPrioritiesRequest(BaseModel):
    """Request body for POST /api/jd/priorities — HR tier decisions."""
    raw_text: str
    skills: list[SkillPriority]
