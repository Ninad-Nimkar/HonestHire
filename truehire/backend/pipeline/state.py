"""
Pipeline state — shared state flowing through the LangGraph pipeline.

Follows langgraph skill: TypedDict with Annotated reducers for list accumulation.
"""

from typing import Annotated, TypedDict
from operator import add

from models.jd import WeightedJD, Skill
from models.candidate import CandidateProfile
from models.scorecard import Scorecard


def merge_dicts(left: dict, right: dict) -> dict:
    """Merge two dicts, right overrides left."""
    return {**left, **right}


class PipelineState(TypedDict):
    """Shared state for the TrueHire analysis pipeline."""

    # Job description
    raw_jd_text: str
    weighted_jd: WeightedJD | None

    # Extracted skills (before HR gate)
    extracted_skills: list[Skill]

    # HR tier decisions received
    hr_decisions_received: bool

    # Candidates
    candidates: Annotated[list[CandidateProfile], lambda a, b: b if b else a]

    # Scorecards accumulate
    scorecards: Annotated[list[Scorecard], lambda a, b: b if b else a]

    # Pipeline tracking
    current_node: str
    progress_pct: float
    error: str | None

    # Job metadata
    job_id: str
    job_title: str
