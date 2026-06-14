"""
Node 4: Link Verifier — checks every URL in candidate profile.
Uses httpx for async HTTP checks and BeautifulSoup for identity matching.
"""

import httpx
from bs4 import BeautifulSoup
from models.candidate import CandidateProfile, LinkCheck


async def link_verifier_node(state: dict) -> dict:
    """Verify all URLs in each candidate's profile."""
    candidates = state.get("candidates", [])
    verified_candidates = []

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        for candidate in candidates:
            if isinstance(candidate, dict):
                candidate = CandidateProfile(**candidate)

            # Collect all URLs to check
            urls = []
            if candidate.linkedin_url:
                urls.append(candidate.linkedin_url)
            if candidate.github_url:
                urls.append(candidate.github_url)
            urls.extend(candidate.other_links or [])

            link_checks = []
            for url in urls:
                check = await _check_link(client, url, candidate.name)
                link_checks.append(check)

            candidate.verification.links_checked = link_checks

            # Update overall authenticity based on link checks
            if link_checks:
                valid_ratio = sum(1 for lc in link_checks if lc.resolves) / len(link_checks)
                identity_ratio = sum(1 for lc in link_checks if lc.identity_match) / len(link_checks)
                candidate.verification.overall_authenticity = round(
                    (valid_ratio * 0.4 + identity_ratio * 0.6), 2
                )

            verified_candidates.append(candidate)

    return {
        "current_node": "link_verifier",
        "candidates": verified_candidates,
    }


async def _check_link(
    client: httpx.AsyncClient, url: str, candidate_name: str
) -> LinkCheck:
    """Check a single URL for resolution and identity match."""
    check = LinkCheck(url=url)

    try:
        response = await client.get(url)
        check.resolves = response.status_code == 200

        if check.resolves and candidate_name:
            # Parse HTML to check if candidate name appears
            soup = BeautifulSoup(response.text, "lxml")
            page_text = soup.get_text().lower()
            name_parts = candidate_name.lower().split()

            # Check if at least first or last name appears
            matches = sum(1 for part in name_parts if part in page_text and len(part) > 2)
            check.identity_match = matches >= 1
            check.authenticity_score = min(1.0, matches / max(len(name_parts), 1))

    except (httpx.HTTPError, httpx.TimeoutException, Exception):
        check.resolves = False
        check.flags.append("URL unreachable or timed out")

    if not check.resolves:
        check.flags.append("Link does not resolve (HTTP error or 404)")
    elif not check.identity_match:
        check.flags.append("Candidate name not found on linked page")

    return check
