"""
Node 3: Profile Parser — parses unstructured CVs into typed CandidateProfile using GPT-4o.
"""

import json
from langchain_openai import ChatOpenAI
from config import settings
from models.candidate import CandidateProfile, Experience


async def profile_parser_node(state: dict) -> dict:
    """Parse each candidate's raw CV into structured fields."""
    candidates = state.get("candidates", [])

    if not candidates:
        return {"current_node": "profile_parser", "error": "No candidates provided"}

    parsed_candidates = []

    for candidate in candidates:
        if isinstance(candidate, dict):
            candidate = CandidateProfile(**candidate)

        # If already has structured data (skills_claimed, experience), keep it
        if candidate.skills_claimed and candidate.experience:
            parsed_candidates.append(candidate)
            continue

        # If raw_cv exists and API key available, parse with LLM
        if candidate.raw_cv and settings.OPENAI_API_KEY:
            try:
                parsed = await _parse_cv_with_llm(candidate)
                parsed_candidates.append(parsed)
            except Exception as e:
                # On failure, keep original
                parsed_candidates.append(candidate)
        else:
            parsed_candidates.append(candidate)

    return {
        "current_node": "profile_parser",
        "candidates": parsed_candidates,
    }


async def _parse_cv_with_llm(candidate: CandidateProfile) -> CandidateProfile:
    """Use GPT-4o to parse unstructured CV text into typed fields."""
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.1,
    )

    prompt = f"""Parse this candidate's CV/resume into structured JSON.

Return valid JSON:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "linkedin_url": "https://...",
  "github_url": "https://...",
  "other_links": ["url1", "url2"],
  "skills_claimed": ["Python", "React", ...],
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "2020-2023",
      "description": "Brief description"
    }}
  ]
}}

CV Text:
---
{candidate.raw_cv[:4000]}
---"""

    response = await llm.ainvoke(prompt)
    content = response.content.strip()

    # Parse JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    data = json.loads(content)

    # Update candidate with parsed data
    candidate.name = data.get("name", candidate.name) or candidate.name
    candidate.email = data.get("email", candidate.email) or candidate.email
    candidate.linkedin_url = data.get("linkedin_url", candidate.linkedin_url) or candidate.linkedin_url
    candidate.github_url = data.get("github_url", candidate.github_url) or candidate.github_url
    candidate.other_links = data.get("other_links", candidate.other_links) or candidate.other_links
    candidate.skills_claimed = data.get("skills_claimed", candidate.skills_claimed) or candidate.skills_claimed
    candidate.experience = [
        Experience(**exp) for exp in data.get("experience", [])
    ] or candidate.experience

    return candidate
