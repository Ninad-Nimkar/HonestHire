import json
from pipeline.state import TrueHireState
from models.candidate import InferredSkill
from config import INFERRED_SKILL_MULTIPLIER

def skill_transfer_node(state: TrueHireState) -> TrueHireState:
    try:
        with open("truehire/data/skill_graph.json", "r") as f:
            skill_graph = json.load(f)
    except Exception:
        skill_graph = {}

    candidates = state.get("candidates", [])
    
    for cand in candidates:
        inferred = []
        for claim in cand.skills_claimed:
            if claim in skill_graph:
                # Direct transfers
                for target, conf in skill_graph[claim].get("direct_transfers", {}).items():
                    inferred.append(InferredSkill(
                        name=target,
                        source_skill=claim,
                        confidence=conf
                    ))
                # Adjacent transfers
                for target, conf in skill_graph[claim].get("adjacent_transfers", {}).items():
                    inferred.append(InferredSkill(
                        name=target,
                        source_skill=claim,
                        confidence=conf
                    ))
        cand.inferred_skills = inferred
        
    return state
