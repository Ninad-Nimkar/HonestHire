from pydantic import BaseModel
from enum import Enum
from typing import List

class Tier(str, Enum):
    blocker = "blocker"
    important = "important"
    nice_to_have = "nice_to_have"

class Skill(BaseModel):
    name: str
    tier: Tier = Tier.nice_to_have
    weight: float = 0.2
    aliases: List[str] = []

class WeightedJD(BaseModel):
    raw_text: str
    skills: List[Skill] = []
