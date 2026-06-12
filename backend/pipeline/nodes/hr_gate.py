from pipeline.state import TrueHireState

def hr_gate_node(state: TrueHireState) -> TrueHireState:
    # In a web app architecture, the HR gate happens between /api/jd/upload and /api/pipeline/run
    # So by the time the pipeline runs, the state already has the prioritized weighted_jd.
    # This node acts as a pass-through/validation step.
    
    jd = state.get("weighted_jd")
    if jd:
        # We could flag vague requirements here if not already done
        pass
        
    return state
