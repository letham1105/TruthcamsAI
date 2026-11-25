from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


VerificationStatus = Literal[
    "processing",
    "success",
    "partial",
    "failed",
]


class VerificationRequest(BaseModel):
    text: str = Field(..., min_length=1)
    claims: list[str] | None = None


class VerificationSessionResponse(BaseModel):
    id: int
    user_id: int | None
    input_type: str
    original_input: str
    status: VerificationStatus
    result: dict[str, Any] | None
    error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class VerificationHistoryItem(BaseModel):
    id: int
    input_type: str
    original_input: str
    status: VerificationStatus
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class VerificationHistoryResponse(BaseModel):
    items: list[VerificationHistoryItem]
    total: int
    limit: int
    offset: int


class DeleteVerificationResponse(BaseModel):
    message: str