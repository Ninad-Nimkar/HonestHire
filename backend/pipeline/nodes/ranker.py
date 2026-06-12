import csv
import json
import os
from pipeline.state import TrueHireState

def ranker_node(state: TrueHireState) -> TrueHireState:
    scorecards = state.get("final_scorecards", [])
    candidates = {c.id: c for c in state.get("candidates", [])}
    
    scorecards.sort(key=lambda x: x.weighted_total, reverse=True)
    
    os.makedirs(os.path.join(os.path.dirname(__file__), "../../output/scorecards"), exist_ok=True)
    
    csv_rows = []
    for rank, sc in enumerate(scorecards, start=1):
        sc.final_rank = rank
        cand = candidates.get(sc.candidate_id)
        name = cand.name if cand else "Unknown"
        
        csv_rows.append({
            "rank": rank,
            "candidate_id": sc.candidate_id,
            "name": name,
            "weighted_score": round(sc.weighted_total, 3),
            "skills_fit": round(sc.scores.skills_fit, 3),
            "experience_relevance": round(sc.scores.experience_relevance, 3),
            "behavioral_signals": round(sc.scores.behavioral_signals, 3),
            "trajectory": round(sc.scores.trajectory, 3),
            "social_credibility": round(sc.scores.social_credibility, 3),
            "confidence": sc.confidence.value,
            "challenger_flags": "|".join(sc.challenger_flags),
            "ai_risk_score": round(sc.ai_risk_score, 3)
        })
        
        path_json = os.path.join(os.path.dirname(__file__), f"../../output/scorecards/{sc.candidate_id}.json")
        with open(path_json, "w") as f:
            f.write(sc.model_dump_json(indent=2))
            
    path_csv = os.path.join(os.path.dirname(__file__), "../../output/ranked_candidates.csv")
    with open(path_csv, "w", newline="", encoding="utf-8") as f:
        if csv_rows:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
            
    return state
