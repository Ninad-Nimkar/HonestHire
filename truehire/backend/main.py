"""
TrueHire FastAPI Application — main entry point.

Serves all API routes and the React frontend in production.
Uses BackgroundTasks for async pipeline execution.
Follows fastapi-pro skill: async-first, Pydantic V2, proper error handling.
"""

import uuid
import time
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import (
    Skill,
    SkillTier,
    WeightedJD,
    JDUploadRequest,
    JDUploadResponse,
    JDPrioritiesRequest,
    CandidateProfile,
    CandidateUploadResponse,
    ScoreAxes,
    ConfidenceLevel,
    Scorecard,
    PipelineStatus,
    PipelineStatusResponse,
    RankedResults,
)
from models.scorecard import NodeStatus, NodeStatusEnum
from config import settings

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TrueHire API",
    description="AI-powered candidate ranking system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory stores (replaced by DB in production)
# ---------------------------------------------------------------------------

# Job store: job_id -> { weighted_jd, candidates, status, scorecards, ... }
jobs: dict[str, dict] = {}

# Temporary stores for multi-step upload flow
_current_jd: dict[str, WeightedJD | None] = {"latest": None}
_current_jd_text: dict[str, str] = {"latest": ""}
_current_candidates: dict[str, list[CandidateProfile]] = {"latest": []}

# Pipeline node definitions for status tracking
PIPELINE_NODES = [
    ("jd_parser", "JD Parser"),
    ("hr_gate", "HR Priority Gate"),
    ("profile_parser", "Profile Parser"),
    ("link_verifier", "Link Verifier"),
    ("github_analyzer", "GitHub Analyzer"),
    ("social_analyzer", "Social Analyzer"),
    ("ai_detector", "AI Detector"),
    ("skill_transfer", "Skill Transfer"),
    ("llm_analyst", "LLM Analyst"),
    ("llm_challenger", "LLM Challenger"),
    ("synthesizer", "Synthesizer"),
    ("ranker", "Ranker"),
]


# ---------------------------------------------------------------------------
# Helper: run pipeline (mock for now, replaced in Phase 8)
# ---------------------------------------------------------------------------

async def _run_pipeline_mock(job_id: str) -> None:
    """Simulate pipeline execution with delays for realistic progress."""
    job = jobs[job_id]

    for i, (node_name, display_name) in enumerate(PIPELINE_NODES):
        # Skip jd_parser and hr_gate (already done before pipeline start)
        if node_name in ("jd_parser", "hr_gate"):
            job["nodes"][i]["status"] = NodeStatusEnum.done
            job["nodes"][i]["elapsed_seconds"] = 0.1
            continue

        job["status"] = PipelineStatus.running
        job["current_node"] = node_name
        job["nodes"][i]["status"] = NodeStatusEnum.running
        job["progress_pct"] = round((i / len(PIPELINE_NODES)) * 100, 1)

        # Simulate processing time
        import asyncio
        await asyncio.sleep(1.5)

        job["nodes"][i]["status"] = NodeStatusEnum.done
        job["nodes"][i]["elapsed_seconds"] = 1.5

    # Generate mock scorecards
    candidates = job.get("candidates", _current_candidates.get("latest", []))
    mock_scorecards = _generate_mock_scorecards(candidates)
    job["scorecards"] = mock_scorecards
    job["status"] = PipelineStatus.complete
    job["progress_pct"] = 100.0
    job["current_node"] = ""
    job["timestamp"] = datetime.now(timezone.utc).isoformat()


def _generate_mock_scorecards(candidates: list[CandidateProfile]) -> list[Scorecard]:
    """Generate realistic mock scorecards for demo purposes."""
    import random
    random.seed(42)

    mock_profiles = [
        {  # Strong genuine match
            "scores": ScoreAxes(
                skills_fit=0.92, experience_relevance=0.88,
                behavioral_signals=0.85, trajectory=0.90, social_credibility=0.87
            ),
            "weighted_total": 0.89,
            "analyst_reasoning": "Strong technical background with verified open-source contributions. "
                                 "Skills align closely with JD requirements. Demonstrated trajectory "
                                 "from IC to tech lead with consistent growth.",
            "challenger_flags": [],
            "confidence": ConfidenceLevel.high,
            "ai_risk_score": 0.12,
        },
        {  # Adjacent fit
            "scores": ScoreAxes(
                skills_fit=0.71, experience_relevance=0.75,
                behavioral_signals=0.82, trajectory=0.85, social_credibility=0.78
            ),
            "weighted_total": 0.76,
            "analyst_reasoning": "Backend engineer with strong transferable skills. Python expertise "
                                 "transfers well to ML engineering. Growing ML side projects show "
                                 "genuine interest and capability.",
            "challenger_flags": ["ML experience is primarily side projects, not production"],
            "confidence": ConfidenceLevel.medium,
            "ai_risk_score": 0.08,
        },
        {  # Underrated candidate
            "scores": ScoreAxes(
                skills_fit=0.65, experience_relevance=0.60,
                behavioral_signals=0.90, trajectory=0.92, social_credibility=0.70
            ),
            "weighted_total": 0.72,
            "analyst_reasoning": "Non-traditional background but exceptional trajectory. Self-taught "
                                 "with real-world projects. Community contributions show deep understanding. "
                                 "Traditional keyword matching would miss this candidate.",
            "challenger_flags": ["No formal CS degree", "Limited corporate experience"],
            "confidence": ConfidenceLevel.medium,
            "ai_risk_score": 0.05,
        },
        {  # AI-generated portfolio
            "scores": ScoreAxes(
                skills_fit=0.78, experience_relevance=0.72,
                behavioral_signals=0.45, trajectory=0.50, social_credibility=0.35
            ),
            "weighted_total": 0.52,
            "analyst_reasoning": "Technical claims appear strong on paper but verification reveals "
                                 "concerning patterns. Portfolio content shows signs of AI generation. "
                                 "GitHub activity is suspiciously uniform.",
            "challenger_flags": [
                "Portfolio README files show zero personal voice",
                "All commit messages are perfectly grammatical and generic",
                "Bulk push detected: 47 commits in 2 days after months of inactivity",
                "Blog posts cover topics with suspiciously complete coverage",
            ],
            "confidence": ConfidenceLevel.needs_review,
            "ai_risk_score": 0.82,
        },
        {  # Keyword-stuffed fake
            "scores": ScoreAxes(
                skills_fit=0.40, experience_relevance=0.35,
                behavioral_signals=0.20, trajectory=0.25, social_credibility=0.15
            ),
            "weighted_total": 0.28,
            "analyst_reasoning": "Profile lists every technology in the JD but lacks depth in any area. "
                                 "Experience descriptions are vague and use identical phrasing. "
                                 "Multiple links are broken or lead to unrelated pages.",
            "challenger_flags": [
                "Claims 12 years of Kubernetes experience (technology is ~10 years old)",
                "LinkedIn profile has 23 connections but claims 'extensive network'",
                "3 of 5 portfolio links return 404",
                "Resume text matches known AI-generated templates",
                "No verifiable open-source contributions despite claiming 'active contributor'",
            ],
            "confidence": ConfidenceLevel.low,
            "ai_risk_score": 0.91,
        },
    ]

    scorecards = []
    for idx, candidate in enumerate(candidates):
        if idx < len(mock_profiles):
            profile = mock_profiles[idx]
        else:
            profile = mock_profiles[0]

        scorecards.append(Scorecard(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            scores=profile["scores"],
            weighted_total=profile["weighted_total"],
            analyst_reasoning=profile["analyst_reasoning"],
            challenger_flags=profile["challenger_flags"],
            confidence=profile["confidence"],
            ai_risk_score=profile["ai_risk_score"],
            final_rank=0,  # Will be assigned after sorting
        ))

    # Sort by weighted_total descending and assign ranks
    scorecards.sort(key=lambda s: s.weighted_total, reverse=True)
    for rank, sc in enumerate(scorecards, 1):
        sc.final_rank = rank

    return scorecards


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/jd/upload", response_model=JDUploadResponse)
async def upload_jd(request: JDUploadRequest):
    """
    Accept raw JD text and return extracted skills.
    In mock mode, returns realistic sample skills.
    """
    _current_jd_text["latest"] = request.raw_text

    # Mock: return realistic extracted skills
    mock_skills = [
        Skill(name="Python", tier=SkillTier.blocker, weight=1.0,
              aliases=["Python3", "CPython"]),
        Skill(name="Machine Learning", tier=SkillTier.blocker, weight=1.0,
              aliases=["ML", "Deep Learning"]),
        Skill(name="PyTorch", tier=SkillTier.important, weight=0.7,
              aliases=["torch"]),
        Skill(name="TensorFlow", tier=SkillTier.important, weight=0.7,
              aliases=["TF", "Keras"]),
        Skill(name="SQL", tier=SkillTier.important, weight=0.7,
              aliases=["PostgreSQL", "MySQL"]),
        Skill(name="Docker", tier=SkillTier.important, weight=0.7,
              aliases=["Containers", "Containerization"]),
        Skill(name="Kubernetes", tier=SkillTier.nice_to_have, weight=0.2,
              aliases=["K8s", "Container Orchestration"],
              flagged_reason="Requires 10+ years experience with a ~10-year-old technology"),
        Skill(name="AWS", tier=SkillTier.nice_to_have, weight=0.2,
              aliases=["Amazon Web Services", "Cloud"]),
        Skill(name="Spark", tier=SkillTier.nice_to_have, weight=0.2,
              aliases=["PySpark", "Apache Spark"]),
        Skill(name="MLOps", tier=SkillTier.important, weight=0.7,
              aliases=["ML Engineering", "Model Deployment"]),
        Skill(name="Data Pipelines", tier=SkillTier.important, weight=0.7,
              aliases=["ETL", "Data Engineering"]),
        Skill(name="Git", tier=SkillTier.blocker, weight=1.0,
              aliases=["GitHub", "Version Control"]),
        Skill(name="Rockstar Developer", tier=SkillTier.nice_to_have, weight=0.2,
              aliases=[],
              flagged_reason="Vague requirement — consider rewriting to specific competencies"),
    ]

    flagged = sum(1 for s in mock_skills if s.flagged_reason)

    return JDUploadResponse(
        title="Senior ML Engineer",
        skills=mock_skills,
        flagged_count=flagged,
    )


@app.post("/api/jd/priorities", response_model=WeightedJD)
async def set_priorities(request: JDPrioritiesRequest):
    """Accept HR tier decisions and return the final WeightedJD."""
    tier_weights = settings.SCORE_WEIGHTS

    skills = []
    for sp in request.skills:
        weight = tier_weights.get(sp.tier.value, 0.5)
        skills.append(Skill(
            name=sp.name,
            tier=sp.tier,
            weight=weight,
            aliases=[],
        ))

    weighted_jd = WeightedJD(
        raw_text=request.raw_text,
        title="Senior ML Engineer",
        skills=skills,
    )
    _current_jd["latest"] = weighted_jd
    return weighted_jd


@app.post("/api/candidates/upload", response_model=CandidateUploadResponse)
async def upload_candidates(file: UploadFile = File(...)):
    """Accept candidate CSV or JSON file and return parsed profiles."""
    content = await file.read()
    text = content.decode("utf-8")

    candidates: list[CandidateProfile] = []

    if file.filename and file.filename.endswith(".json"):
        data = json.loads(text)
        if isinstance(data, list):
            for item in data:
                candidates.append(CandidateProfile(**item))
        else:
            raise HTTPException(400, "JSON must be an array of candidate objects")
    elif file.filename and file.filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(text))
        for i, row in enumerate(reader):
            candidates.append(CandidateProfile(
                id=row.get("id", f"cand-{i+1}"),
                name=row.get("name", ""),
                email=row.get("email", ""),
                raw_cv=row.get("raw_cv", ""),
                linkedin_url=row.get("linkedin_url", ""),
                github_url=row.get("github_url", ""),
                skills_claimed=[s.strip() for s in row.get("skills", "").split(",") if s.strip()],
            ))
    else:
        raise HTTPException(400, "File must be .json or .csv")

    _current_candidates["latest"] = candidates

    return CandidateUploadResponse(count=len(candidates), candidates=candidates)


@app.post("/api/pipeline/run")
async def run_pipeline(background_tasks: BackgroundTasks):
    """Start the analysis pipeline. Returns a job_id for status polling."""
    job_id = str(uuid.uuid4())[:8]

    # Initialize job status
    nodes = [
        NodeStatus(name=name, display_name=display, status=NodeStatusEnum.waiting)
        for name, display in PIPELINE_NODES
    ]

    candidates = _current_candidates.get("latest", [])

    jobs[job_id] = {
        "status": PipelineStatus.pending,
        "current_node": "",
        "progress_pct": 0.0,
        "nodes": [n.model_dump() for n in nodes],
        "weighted_jd": _current_jd.get("latest"),
        "candidates": candidates,
        "scorecards": [],
        "timestamp": "",
        "job_title": "Senior ML Engineer",
    }

    # Run pipeline in background
    background_tasks.add_task(_run_pipeline_mock, job_id)

    return {"job_id": job_id, "status": "started"}


@app.get("/api/pipeline/status/{job_id}", response_model=PipelineStatusResponse)
async def pipeline_status(job_id: str):
    """Get current pipeline status for polling."""
    if job_id not in jobs:
        raise HTTPException(404, f"Job {job_id} not found")

    job = jobs[job_id]

    return PipelineStatusResponse(
        job_id=job_id,
        status=job["status"],
        current_node=job["current_node"],
        progress_pct=job["progress_pct"],
        nodes=[NodeStatus(**n) for n in job["nodes"]],
    )


@app.get("/api/results/{job_id}", response_model=RankedResults)
async def get_results(job_id: str):
    """Get full ranked results for a completed pipeline run."""
    if job_id not in jobs:
        raise HTTPException(404, f"Job {job_id} not found")

    job = jobs[job_id]
    if job["status"] != PipelineStatus.complete:
        raise HTTPException(400, "Pipeline not yet complete")

    return RankedResults(
        job_id=job_id,
        job_title=job.get("job_title", ""),
        total_candidates=len(job["scorecards"]),
        timestamp=job.get("timestamp", ""),
        scorecards=job["scorecards"],
    )


@app.get("/api/results/{job_id}/csv")
async def download_csv(job_id: str):
    """Download ranked candidates as CSV."""
    if job_id not in jobs:
        raise HTTPException(404, f"Job {job_id} not found")

    job = jobs[job_id]
    if job["status"] != PipelineStatus.complete:
        raise HTTPException(400, "Pipeline not yet complete")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Candidate ID", "Name", "Weighted Total",
        "Skills Fit", "Experience Relevance", "Behavioral Signals",
        "Trajectory", "Social Credibility", "AI Risk Score",
        "Confidence", "Challenger Flags",
    ])

    for sc in job["scorecards"]:
        sc_obj = sc if isinstance(sc, Scorecard) else Scorecard(**sc) if isinstance(sc, dict) else sc
        writer.writerow([
            sc_obj.final_rank,
            sc_obj.candidate_id,
            sc_obj.candidate_name,
            f"{sc_obj.weighted_total:.2f}",
            f"{sc_obj.scores.skills_fit:.2f}",
            f"{sc_obj.scores.experience_relevance:.2f}",
            f"{sc_obj.scores.behavioral_signals:.2f}",
            f"{sc_obj.scores.trajectory:.2f}",
            f"{sc_obj.scores.social_credibility:.2f}",
            f"{sc_obj.ai_risk_score:.2f}",
            sc_obj.confidence.value,
            "; ".join(sc_obj.challenger_flags),
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ranked_candidates_{job_id}.csv"},
    )


@app.get("/api/candidate/{candidate_id}/scorecard")
async def get_candidate_scorecard(candidate_id: str):
    """Get the full scorecard for a specific candidate."""
    # Search across all jobs
    for job in jobs.values():
        for sc in job.get("scorecards", []):
            sc_obj = sc if isinstance(sc, Scorecard) else Scorecard(**sc) if isinstance(sc, dict) else sc
            if sc_obj.candidate_id == candidate_id:
                return sc_obj

    raise HTTPException(404, f"Scorecard for candidate {candidate_id} not found")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
