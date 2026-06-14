"""
TrueHire configuration — loads from environment variables via pydantic-settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    OPENAI_API_KEY: str = ""
    GITHUB_TOKEN: str = ""
    PROXYCURL_KEY: str = ""

    # OpenAI
    OPENAI_MODEL: str = "gpt-4o"

    # Scoring weights by skill tier
    SCORE_WEIGHTS: dict[str, float] = {
        "blocker": 1.0,
        "important": 0.7,
        "nice_to_have": 0.2,
    }

    # Inferred skill confidence multipliers
    INFERRED_SKILL_MULTIPLIER: dict[str, float] = {
        "direct": 0.85,
        "adjacent": 0.65,
        "stretch": 0.4,
    }

    # Thresholds
    AI_RISK_THRESHOLD: float = 0.7
    DEBATE_DISAGREEMENT_THRESHOLD: float = 0.2

    # Frontend polling interval (ms)
    PIPELINE_POLL_INTERVAL_MS: int = 2000

    # Paths
    OUTPUT_DIR: str = str(Path(__file__).resolve().parent / "output")
    DATA_DIR: str = str(Path(__file__).resolve().parent / "data")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
