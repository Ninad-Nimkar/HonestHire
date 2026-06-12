import json
import os
from pipeline.state import TrueHireState
from models.candidate import InferredSkill

def skill_transfer_node(state: TrueHireState) -> TrueHireState:
    try:
        path = os.path.join(os.path.dirname(__file__), "../../data/skill_graph.json")
        with open(path, "r") as f:
            skill_graph = json.load(f)
    except Exception:
        skill_graph = {}

    candidates = state.get("candidates", [])
    
    for cand in candidates:
        inferred = []
        for claim in cand.skills_claimed:
            if claim in skill_graph:
                for target, conf in skill_graph[claim].get("direct_transfers", {}).items():
                    inferred.append(InferredSkill(name=target, source_skill=claim, confidence=conf))
                for target, conf in skill_graph[claim].get("adjacent_transfers", {}).items():
                    inferred.append(InferredSkill(name=target, source_skill=claim, confidence=conf))
        cand.inferred_skills = inferred
        
    return state
