"""
Scorecard and pipeline status models.

Follows pydantic-models-py skill: typed enums, validated ranges, clear docs.
"""

from enum import Enum
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Confidence level for a candidate's scorecard."""
    high = "high"
    medium = "medium"
    low = "low"
    needs_review = "needs_review"


class ScoreAxes(BaseModel):
    """The 5 scoring axes for candidate evaluation."""
    skills_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    experience_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    behavioral_signals: float = Field(default=0.0, ge=0.0, le=1.0)
    trajectory: float = Field(default=0.0, ge=0.0, le=1.0)
    social_credibility: float = Field(default=0.0, ge=0.0, le=1.0)


class Scorecard(BaseModel):
    """Full scorecard for a single candidate."""
    candidate_id: str
    candidate_name: str = ""
    scores: ScoreAxes = Field(default_factory=ScoreAxes)
    weighted_total: float = Field(default=0.0, ge=0.0, le=1.0)
    analyst_reasoning: str = ""
    challenger_flags: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.medium
    ai_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    final_rank: int = Field(default=0, ge=0)
    excluded: bool = False
    exclusion_reason: str = ""


class NodeStatusEnum(str, Enum):
    """Status of a single pipeline node."""
    waiting = "waiting"
    running = "running"
    done = "done"
    error = "error"
    skipped = "skipped"


class NodeStatus(BaseModel):
    """Status of a single pipeline node."""
    name: str
    display_name: str = ""
    status: NodeStatusEnum = NodeStatusEnum.waiting
    elapsed_seconds: float = 0.0
    error_message: str | None = None


class PipelineStatus(str, Enum):
    """Overall pipeline status."""
    pending = "pending"
    running = "running"
    complete = "complete"
    error = "error"


class PipelineStatusResponse(BaseModel):
    """Response from GET /api/pipeline/status/{id}."""
    job_id: str
    status: PipelineStatus = PipelineStatus.pending
    current_node: str = ""
    progress_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    nodes: list[NodeStatus] = Field(default_factory=list)
    error_message: str | None = None


class RankedResults(BaseModel):
    """Response from GET /api/results/{job_id}."""
    job_id: str
    job_title: str = ""
    total_candidates: int = 0
    timestamp: str = ""
    scorecards: list[Scorecard] = Field(default_factory=list)
