"""
Node 1: JD Parser — extracts skills from raw job description text using GPT-4o.
"""

import json
from langchain_openai import ChatOpenAI
from config import settings
from models.jd import Skill, SkillTier


async def jd_parser_node(state: dict) -> dict:
    """Extract discrete skills from raw JD text using LLM."""
    raw_text = state.get("raw_jd_text", "")

    if not raw_text:
        return {"current_node": "jd_parser", "error": "No JD text provided"}

    if not settings.OPENAI_API_KEY:
        # Fallback: return empty skills for demo
        return {
            "current_node": "jd_parser",
            "extracted_skills": [],
            "job_title": "Untitled Position",
        }

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.1,
    )

    prompt = f"""Analyze this job description and extract all required skills/technologies.
For each skill, suggest a priority tier and identify if any requirements seem inflated.

Return valid JSON with this structure:
{{
  "title": "extracted job title",
  "skills": [
    {{
      "name": "Skill Name",
      "tier": "blocker|important|nice_to_have",
      "aliases": ["alias1", "alias2"],
      "flagged_reason": "reason or null"
    }}
  ]
}}

Flag requirements that are:
- Vague terms like "rockstar", "ninja", "wizard"
- Years required > technology age
- Unrealistic combinations

Job Description:
---
{raw_text}
---"""

    response = await llm.ainvoke(prompt)
    content = response.content.strip()

    # Parse JSON from response
    try:
        # Handle markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)
        skills = []
        tier_weights = settings.SCORE_WEIGHTS

        for s in data.get("skills", []):
            tier = SkillTier(s.get("tier", "important"))
            skills.append(Skill(
                name=s["name"],
                tier=tier,
                weight=tier_weights.get(tier.value, 0.7),
                aliases=s.get("aliases", []),
                flagged_reason=s.get("flagged_reason"),
            ))

        return {
            "current_node": "jd_parser",
            "extracted_skills": skills,
            "job_title": data.get("title", "Untitled Position"),
        }
    except (json.JSONDecodeError, KeyError) as e:
        return {
            "current_node": "jd_parser",
            "extracted_skills": [],
            "job_title": "Untitled Position",
            "error": f"Failed to parse LLM response: {e}",
        }
