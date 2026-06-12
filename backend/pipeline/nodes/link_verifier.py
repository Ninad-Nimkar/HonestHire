import httpx
from pipeline.state import TrueHireState
from models.candidate import LinkCheck, VerificationResult

def link_verifier_node(state: TrueHireState) -> TrueHireState:
    candidates = state.get("candidates", [])
    
    for cand in candidates:
        if cand.verification is None:
            cand.verification = VerificationResult()
            
        urls = [cand.linkedin_url, cand.github_url] + cand.other_links
        urls = [u for u in urls if u]
        
        for url in urls:
            try:
                resp = httpx.get(url, timeout=5.0)
                resolves = resp.status_code < 400
            except Exception:
                resolves = False
                
            identity_match = False
            if resolves and cand.name.lower().split()[0] in url.lower():
                identity_match = True
                
            check = LinkCheck(
                url=url,
                resolves=resolves,
                identity_match=identity_match,
                authenticity_score=0.9 if resolves else 0.0,
                flags=["Unresolvable URL"] if not resolves else []
            )
            cand.verification.links_checked.append(check)
            
    return state
