"""
Node 7: AI Detector — heuristic AI content detection (no external APIs).
Analyzes text patterns across portfolios, blog posts, commit messages.
"""

import re
from models.candidate import CandidateProfile


# Heuristic signals for AI-generated content
AI_SIGNALS = {
    "no_personal_voice": {
        "description": "No personal voice or opinions detected",
        "weight": 0.15,
    },
    "suspiciously_complete": {
        "description": "Suspiciously complete coverage of topics",
        "weight": 0.12,
    },
    "zero_typos": {
        "description": "Zero typos across large body of text",
        "weight": 0.08,
    },
    "perfect_docs": {
        "description": "Every function perfectly documented with identical patterns",
        "weight": 0.10,
    },
    "generic_commits": {
        "description": "Commit messages all generic and perfectly grammatical",
        "weight": 0.10,
    },
    "bulk_push": {
        "description": "Large volume of content pushed in very short time",
        "weight": 0.15,
    },
    "template_language": {
        "description": "Uses AI-template phrases like 'In this comprehensive guide'",
        "weight": 0.12,
    },
    "uniform_style": {
        "description": "Unnaturally uniform writing style across all content",
        "weight": 0.08,
    },
}

# Common AI template phrases
AI_TEMPLATE_PHRASES = [
    "in this comprehensive",
    "let's dive",
    "it's worth noting",
    "it's important to note",
    "in today's rapidly evolving",
    "leveraging cutting-edge",
    "in the ever-changing landscape",
    "robust and scalable",
    "seamless integration",
    "comprehensive guide",
    "delve into",
    "in conclusion",
    "without further ado",
    "game-changer",
    "paradigm shift",
]


async def ai_detector_node(state: dict) -> dict:
    """Detect AI-generated content in candidate profiles."""
    candidates = state.get("candidates", [])
    analyzed = []

    for candidate in candidates:
        if isinstance(candidate, dict):
            candidate = CandidateProfile(**candidate)

        flags = []
        risk_score = 0.0

        # Analyze raw CV text
        cv_text = candidate.raw_cv or ""
        if cv_text:
            cv_flags, cv_score = _analyze_text(cv_text)
            flags.extend(cv_flags)
            risk_score += cv_score * 0.4  # CV contributes 40%

        # Check GitHub signals
        github = candidate.verification.github_signals
        if github.bulk_push_detected:
            flags.append(AI_SIGNALS["bulk_push"]["description"])
            risk_score += AI_SIGNALS["bulk_push"]["weight"]

        if github.ai_code_signals:
            for signal in github.ai_code_signals:
                flags.append(signal)
                risk_score += 0.05

        # Check for generic commit messages
        if github.commit_count > 0 and github.commit_span_days < 5:
            flags.append(
                f"All {github.commit_count} commits within {github.commit_span_days} days"
            )
            risk_score += AI_SIGNALS["generic_commits"]["weight"]

        # Cap at 1.0
        risk_score = min(1.0, risk_score)

        candidate.ai_risk_score = round(risk_score, 2)
        candidate.ai_risk_flags = flags

        analyzed.append(candidate)

    return {"current_node": "ai_detector", "candidates": analyzed}


def _analyze_text(text: str) -> tuple[list[str], float]:
    """Analyze text for AI-generation heuristic signals."""
    flags = []
    score = 0.0

    if not text or len(text) < 100:
        return flags, score

    text_lower = text.lower()

    # 1. Check for AI template phrases
    template_hits = sum(1 for phrase in AI_TEMPLATE_PHRASES if phrase in text_lower)
    if template_hits >= 3:
        flags.append(AI_SIGNALS["template_language"]["description"])
        score += AI_SIGNALS["template_language"]["weight"]
    elif template_hits >= 1:
        score += AI_SIGNALS["template_language"]["weight"] * 0.5

    # 2. Check for zero typos in long text (suspicious if > 2000 chars with 0 common patterns)
    if len(text) > 2000:
        # Check for natural imperfections
        has_contractions = bool(re.search(r"\b(don't|won't|can't|I'm|I've|didn't)\b", text))
        has_informal = bool(re.search(r"\b(kinda|gonna|wanna|btw|tbh|imo)\b", text_lower))

        if not has_contractions and not has_informal:
            flags.append(AI_SIGNALS["no_personal_voice"]["description"])
            score += AI_SIGNALS["no_personal_voice"]["weight"]

    # 3. Check for suspiciously uniform sentence length
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) > 10:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        if variance < 15:  # Very low variance = suspiciously uniform
            flags.append(AI_SIGNALS["uniform_style"]["description"])
            score += AI_SIGNALS["uniform_style"]["weight"]

    return flags, score
