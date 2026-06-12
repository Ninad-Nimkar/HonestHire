import json
import os
import uuid
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel

from models.jd import WeightedJD, Skill, Tier
from models.candidate import CandidateProfile
from pipeline.state import TrueHireState
from pipeline.graph import build_graph

app = FastAPI(title="TrueHire API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory storage for jobs (mock DB)
jobs = {}

class JDUploadRequest(BaseModel):
    text: str

class JDResponse(BaseModel):
    skills: List[Dict[str, Any]]

class RunRequest(BaseModel):
    jd: Dict[str, Any]
    candidates: List[Dict[str, Any]]

@app.post("/api/jd/upload")
def upload_jd(req: JDUploadRequest):
    # MOCK implementation for now
    return JDResponse(skills=[
        {"name": "Python", "tier": "important", "weight": 0.7, "aliases": []},
        {"name": "React", "tier": "blocker", "weight": 1.0, "aliases": []},
        {"name": "Rockstar attitude", "tier": "nice_to_have", "weight": 0.2, "aliases": [], "flagged": True}
    ])

@app.post("/api/jd/priorities")
def set_priorities(jd: WeightedJD):
    # Endpoint to finalize priorities and get the parsed Pydantic object
    return jd

@app.post("/api/candidates/upload")
async def upload_candidates(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    
    try:
        data = json.loads(text)
        if isinstance(data, list):
            raw_cvs = [item.get("raw_cv", "") for item in data if "raw_cv" in item]
            return {"status": "ok", "count": len(raw_cvs), "raw_cvs": raw_cvs}
    except json.JSONDecodeError:
        pass
        
    return {"status": "ok", "count": 1, "raw_cvs": [text]}

def run_pipeline_task(job_id: str, state: TrueHireState):
    graph = build_graph()
    
    # We will step through the graph to update status
    # In LangGraph 0.0.x, we use graph.stream()
    
    jobs[job_id]["status"] = "running"
    
    try:
        final_state = state
        node_idx = 1
        for output in graph.stream(state):
            # output is a dict like {"node_name": new_state}
            node_name = list(output.keys())[0]
            jobs[job_id]["node"] = node_name
            jobs[job_id]["progress"] = int((node_idx / 12) * 100)
            node_idx += 1
            final_state = output[node_name]
            
        jobs[job_id]["status"] = "complete"
        # We store the final candidates in memory just for the demo
        jobs[job_id]["result_state"] = final_state
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)

@app.post("/api/pipeline/run")
def run_pipeline(req: RunRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    state: TrueHireState = {
        "raw_jd": req.jd.get("raw_text", ""),
        "weighted_jd": WeightedJD(**req.jd),
        "raw_cvs": [c.get("raw_cv", "") for c in req.candidates],
        "candidates": [],
        "llm_a_scorecards": {},
        "llm_b_flags": {},
        "final_scorecards": []
    }
    
    jobs[job_id] = {"status": "starting", "node": "init", "progress": 0}
    background_tasks.add_task(run_pipeline_task, job_id, state)
    return {"job_id": job_id}

@app.get("/api/pipeline/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/api/results/{job_id}")
def get_results(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "complete":
        raise HTTPException(status_code=400, detail="Results not ready")
    
    state = jobs[job_id].get("result_state", {})
    scorecards = state.get("final_scorecards", [])
    candidates = {c.id: c for c in state.get("candidates", [])}
    
    out_candidates = []
    for sc in scorecards:
        cand = candidates.get(sc.candidate_id)
        out_candidates.append({
            "candidate_id": sc.candidate_id,
            "name": cand.name if cand else "Unknown",
            "final_rank": sc.final_rank,
            "weighted_total": sc.weighted_total,
            "scores": sc.scores.model_dump(),
            "confidence": sc.confidence.value,
            "ai_risk_score": sc.ai_risk_score,
            "verification": cand.verification.model_dump() if cand and cand.verification else {},
            "challenger_flags": sc.challenger_flags,
            "analyst_reasoning": sc.analyst_reasoning
        })
        
    return {"candidates": out_candidates}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
