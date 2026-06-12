import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PROXYCURL_KEY = os.getenv("PROXYCURL_KEY")

OPENAI_MODEL = "gpt-4o"

SCORE_WEIGHTS = {
    "blocker": 1.0,
    "important": 0.7,
    "nice_to_have": 0.2
}

INFERRED_SKILL_MULTIPLIER = {
    "direct": 0.85,
    "adjacent": 0.65,
    "stretch": 0.4
}

AI_RISK_THRESHOLD = 0.7
DEBATE_DISAGREEMENT_THRESHOLD = 0.2
PIPELINE_POLL_INTERVAL_MS = 2000
