from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator


REQUEST_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$"
NAME_KEY_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9-]{0,127}$"
CORE_PATTERN = r"^Z[A-Z0-9]{2,7}$"
LANE_PATTERN = r"^[0-9]{5}$"
Z_CODE_PATTERN = r"^Z[A-Z0-9]{2,7}-[0-9]{5}-[0-9]{6}-[0-9]{3}$"


class AllocateRequest(BaseModel):
    request_id: str = Field(pattern=REQUEST_ID_PATTERN)
    name_key: str = Field(pattern=NAME_KEY_PATTERN)
    z_knowledge_core: str = Field(pattern=CORE_PATTERN)
    knowledge_lane: str = Field(pattern=LANE_PATTERN)
    page_type: str = Field(min_length=1, max_length=64)
    requested_by: str = Field(min_length=1, max_length=64)


class ConfirmRequest(BaseModel):
    z_code: str = Field(pattern=Z_CODE_PATTERN)
    status: Literal["active", "failed"] = "active"
    notion_url: HttpUrl | None = None
    reason: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_confirmation(self) -> "ConfirmRequest":
        if self.status == "active" and self.notion_url is None:
            raise ValueError("notion_url is required when status is active")
        if self.status == "failed" and not self.reason:
            raise ValueError("reason is required when status is failed")
        return self


class ReassignTopicRequest(BaseModel):
    name_key: str = Field(pattern=NAME_KEY_PATTERN)
    new_z_knowledge_core: str = Field(pattern=CORE_PATTERN)
    new_knowledge_lane: str = Field(pattern=LANE_PATTERN)
    reason: str = Field(min_length=3, max_length=1000)


class ResolveReviewRequest(BaseModel):
    resolution: Literal["dismissed", "retry_allowed"]
    notes: str = Field(min_length=3, max_length=1000)


class OutboxResultRequest(BaseModel):
    error: str | None = Field(default=None, max_length=2000)

