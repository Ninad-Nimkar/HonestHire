from pipeline.state import TrueHireState
from models.scorecard import ConfidenceLevel

def synthesizer_node(state: TrueHireState) -> TrueHireState:
    scorecards = state.get("llm_a_scorecards", {})
    flags = state.get("llm_b_flags", {})
    
    final_scorecards = []
    
    for cid, scorecard in scorecards.items():
        challenger_flags = flags.get(cid, [])
        scorecard.challenger_flags = challenger_flags
        
        # Simple penalty for flags
        penalty = len(challenger_flags) * 0.05
        
        s = scorecard.scores
        raw_total = (
            s.skills_fit * 0.4 +
            s.experience_relevance * 0.3 +
            s.behavioral_signals * 0.1 +
            s.trajectory * 0.1 +
            s.social_credibility * 0.1
        )
        
        scorecard.weighted_total = max(0.0, raw_total - penalty)
        
        if len(challenger_flags) == 0:
            scorecard.confidence = ConfidenceLevel.high
        elif len(challenger_flags) <= 2:
            scorecard.confidence = ConfidenceLevel.medium
        else:
            scorecard.confidence = ConfidenceLevel.needs_review
            
        final_scorecards.append(scorecard)
        
    state["final_scorecards"] = final_scorecards
    return state
