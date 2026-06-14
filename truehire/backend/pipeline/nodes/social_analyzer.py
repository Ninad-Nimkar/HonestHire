"""
Node 6: Social Analyzer — analyzes LinkedIn/Twitter public profiles.
Graceful fallback when profiles are inaccessible.
"""

import httpx
from bs4 import BeautifulSoup
from models.candidate import CandidateProfile, SocialSignals


async def social_analyzer_node(state: dict) -> dict:
    """Analyze social presence for each candidate."""
    candidates = state.get("candidates", [])
    analyzed = []

    for candidate in candidates:
        if isinstance(candidate, dict):
            candidate = CandidateProfile(**candidate)

        signals = SocialSignals()

        # LinkedIn analysis
        if candidate.linkedin_url:
            signals = await _analyze_linkedin(candidate.linkedin_url, candidate.name, signals)

        # Cross-reference with GitHub
        if candidate.verification.github_signals.username:
            github_langs = set(candidate.verification.github_signals.top_languages)
            claimed_skills = set(s.lower() for s in candidate.skills_claimed)

            # Check if GitHub activity matches claimed skills
            lang_overlap = github_langs.intersection(claimed_skills)
            if github_langs and not lang_overlap:
                signals.notes.append(
                    "GitHub languages don't overlap with claimed skills"
                )
                signals.cross_reference_match = False
            elif lang_overlap:
                signals.cross_reference_match = True
                signals.notes.append(
                    f"GitHub activity confirms: {', '.join(lang_overlap)}"
                )

        candidate.social_signals = signals
        candidate.verification.social_signals = signals
        analyzed.append(candidate)

    return {"current_node": "social_analyzer", "candidates": analyzed}


async def _analyze_linkedin(
    url: str, name: str, signals: SocialSignals
) -> SocialSignals:
    """Attempt to analyze LinkedIn public profile."""
    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; TrueHire/1.0)"},
        ) as client:
            response = await client.get(url)

            if response.status_code == 200:
                signals.linkedin_accessible = True
                soup = BeautifulSoup(response.text, "lxml")
                page_text = soup.get_text().lower()

                # Check if name appears
                if name.lower() in page_text:
                    signals.notes.append("LinkedIn profile matches candidate name")

                # Check for recent activity indicators
                if "posted" in page_text or "shared" in page_text:
                    signals.linkedin_post_recency = "recent"
                    signals.notes.append("Shows recent LinkedIn activity")
            else:
                signals.linkedin_accessible = False
                signals.notes.append(
                    f"LinkedIn profile returned status {response.status_code}"
                )
    except (httpx.HTTPError, Exception):
        signals.linkedin_accessible = False
        signals.notes.append("LinkedIn profile not accessible (login wall or error)")

    return signals
