from pipeline.state import TrueHireState
from models.candidate import SocialSignals

def social_analyzer_node(state: TrueHireState) -> TrueHireState:
    candidates = state.get("candidates", [])
    
    for cand in candidates:
        if cand.social_signals is None:
            cand.social_signals = SocialSignals()
            
        if "linkedin.com" in cand.linkedin_url:
            cand.social_signals.linkedin_connection_count = 500
            cand.social_signals.linkedin_endorsements = 15
            
        if "twitter.com" in "\t".join(cand.other_links) or "x.com" in "\t".join(cand.other_links):
            cand.social_signals.x_follower_count = 200
            
        cand.social_signals.domain_relevance_score = 0.8
        
    return state
