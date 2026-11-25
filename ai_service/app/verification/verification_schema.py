from typing import Literal
from pydantic import BaseModel


VerificationLabel = Literal[
    "supported",
    "refuted",
    "not_enough_information",
]


class VerificationResult(BaseModel):
    label: VerificationLabel
    confidence: float
    scores: dict[str, float]
