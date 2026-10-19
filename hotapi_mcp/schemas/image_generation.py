from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class ZImageSpicyError(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = None
    code: str | None = None
    message: str | None = None


class ZImageSpicyData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    object: str
    status: str = Field(
        description="Lifecycle status: pending, queued, processing, succeeded, failed, cancelled or expired. Terminal states: succeeded, failed, cancelled, expired."
    )
    model: str
    task_kind: str
    input: dict[str, Any]
    output: dict[str, Any] | None = Field(
        default=None, description="Result payload, present once status=succeeded. Contains hosted asset URLs."
    )
    error: ZImageSpicyError | None = None
    estimated_credits_cost: int = Field(description="Credits charged up-front at creation (1000 credits = $1).")
    actual_credits_cost: int | None = Field(default=None, description="Final credits charged after settlement.")
    webhook_url: str | None = None
    api_key_id: str | None = None
    created_at: int = Field(description="Unix seconds.")
    queued_at: int | None = Field(default=None, description="Unix seconds.")
    started_at: int | None = Field(default=None, description="Unix seconds.")
    completed_at: int | None = Field(default=None, description="Unix seconds.")
    expires_at: int = Field(description="Unix seconds; result and asset retention deadline.")
    reference_video_seconds: float | None = None


class ZImageSpicyResult(ToolResult):
    data: ZImageSpicyData | None = None
