"""
Node 5: GitHub Analyzer — analyzes GitHub profile for authenticity signals.
Uses GitHub REST API: commits, events, repo list.
"""

import httpx
from models.candidate import CandidateProfile, GitHubSignals
from config import settings


async def github_analyzer_node(state: dict) -> dict:
    """Analyze each candidate's GitHub profile."""
    candidates = state.get("candidates", [])
    analyzed = []

    for candidate in candidates:
        if isinstance(candidate, dict):
            candidate = CandidateProfile(**candidate)

        if candidate.github_url:
            username = _extract_username(candidate.github_url)
            if username:
                signals = await _analyze_github(username)
                candidate.verification.github_signals = signals

        analyzed.append(candidate)

    return {"current_node": "github_analyzer", "candidates": analyzed}


def _extract_username(github_url: str) -> str | None:
    """Extract GitHub username from URL."""
    url = github_url.rstrip("/")
    if "github.com/" in url:
        parts = url.split("github.com/")
        if len(parts) > 1:
            return parts[1].split("/")[0].split("?")[0]
    return None


async def _analyze_github(username: str) -> GitHubSignals:
    """Fetch and analyze GitHub profile data."""
    signals = GitHubSignals(username=username)
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 1. User info + repos
            user_resp = await client.get(
                f"https://api.github.com/users/{username}", headers=headers
            )
            if user_resp.status_code != 200:
                return signals

            user_data = user_resp.json()
            signals.public_repos = user_data.get("public_repos", 0)

            # 2. Get recent repos
            repos_resp = await client.get(
                f"https://api.github.com/users/{username}/repos",
                headers=headers,
                params={"sort": "updated", "per_page": 10},
            )
            if repos_resp.status_code == 200:
                repos = repos_resp.json()
                languages = set()
                for repo in repos:
                    if repo.get("language"):
                        languages.add(repo["language"])
                signals.top_languages = list(languages)[:10]

                # Check for collaboration
                for repo in repos[:5]:
                    contributors_resp = await client.get(
                        repo.get("contributors_url", ""),
                        headers=headers,
                        params={"per_page": 5},
                    )
                    if contributors_resp.status_code == 200:
                        contributors = contributors_resp.json()
                        if isinstance(contributors, list) and len(contributors) > 1:
                            signals.real_collaboration = True
                            break

            # 3. Get recent events for commit analysis
            events_resp = await client.get(
                f"https://api.github.com/users/{username}/events",
                headers=headers,
                params={"per_page": 100},
            )
            if events_resp.status_code == 200:
                events = events_resp.json()
                push_events = [e for e in events if e.get("type") == "PushEvent"]

                total_commits = 0
                commit_dates = []
                commit_messages = []

                for event in push_events:
                    commits = event.get("payload", {}).get("commits", [])
                    total_commits += len(commits)
                    commit_dates.append(event.get("created_at", ""))
                    for c in commits:
                        commit_messages.append(c.get("message", ""))

                signals.commit_count = total_commits

                # Calculate commit span
                if len(commit_dates) >= 2:
                    from datetime import datetime
                    try:
                        dates = [datetime.fromisoformat(d.replace("Z", "+00:00"))
                                 for d in commit_dates if d]
                        if dates:
                            span = (max(dates) - min(dates)).days
                            signals.commit_span_days = span
                    except (ValueError, TypeError):
                        pass

                # Detect bulk pushes (many commits in short period)
                if total_commits > 30 and signals.commit_span_days < 3:
                    signals.bulk_push_detected = True
                    signals.ai_code_signals.append(
                        f"Bulk push detected: {total_commits} commits in {signals.commit_span_days} days"
                    )

                # Check commit message quality
                generic_patterns = [
                    "update", "fix", "add", "initial commit", "wip",
                    "update readme", "minor changes", "bug fix",
                ]
                if commit_messages:
                    generic_count = sum(
                        1 for msg in commit_messages[:20]
                        if msg.lower().strip() in generic_patterns
                    )
                    if generic_count > len(commit_messages[:20]) * 0.6:
                        signals.ai_code_signals.append(
                            "Majority of commit messages are generic/uninformative"
                        )

    except (httpx.HTTPError, Exception):
        pass

    return signals
