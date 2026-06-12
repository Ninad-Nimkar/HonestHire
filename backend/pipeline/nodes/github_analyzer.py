import os
import httpx
from datetime import datetime
from langchain_openai import ChatOpenAI
from pipeline.state import TrueHireState
from models.candidate import GitHubSignals
from pydantic import BaseModel, Field

class AIMessageCheck(BaseModel):
    is_ai: bool = Field(description="True if messages look AI-generated")
    signals: list[str] = Field(description="Specific reasons")

def github_analyzer_node(state: TrueHireState) -> TrueHireState:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"), 
        temperature=0, 
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    structured_llm = llm.with_structured_output(AIMessageCheck)
    
    candidates = state.get("candidates", [])
    for cand in candidates:
        if not cand.github_url:
            continue
            
        username = cand.github_url.rstrip("/").split("/")[-1]
        
        try:
            events_resp = httpx.get(f"https://api.github.com/users/{username}/events", headers=headers, timeout=5.0)
            events = events_resp.json() if events_resp.status_code == 200 else []
        except:
            events = []
            
        commits = []
        commit_dates = []
        if isinstance(events, list):
            for ev in events:
                if ev.get("type") == "PushEvent":
                    created_at = ev.get("created_at")
                    if created_at:
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        commit_dates.append(dt)
                    for c in ev.get("payload", {}).get("commits", []):
                        commits.append(c.get("message", ""))
                    
        total_commits = len(commits)
        span_days = 0
        if commit_dates:
            span_days = (max(commit_dates) - min(commit_dates)).days
            
        bulk_push = (total_commits > 50 and span_days < 7)
        
        ai_signals = []
        if total_commits > 0:
            sample_messages = "\\n".join(commits[:10])
            prompt = f"Do these commit messages look human or AI-generated? Look for: generic phrasing, perfect grammar on every message, no casual/abbreviated messages, no frustration markers.\n\nMessages:\n{sample_messages}"
            try:
                res = structured_llm.invoke(prompt)
                if res.is_ai:
                    ai_signals.extend(res.signals)
            except Exception:
                pass
                
        gh_signals = GitHubSignals(
            commit_count=total_commits,
            commit_span_days=span_days,
            bulk_push_detected=bulk_push,
            ai_code_signals=ai_signals,
            real_collaboration=True 
        )
        
        if cand.verification:
            cand.verification.github_signals = gh_signals
            
    return state
