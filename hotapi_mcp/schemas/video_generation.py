from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class Seedance20SpicyTextToVideoError(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = None
    code: str | None = None
    message: str | None = None


class Seedance20SpicyTextToVideoData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    object: str
    status: str = Field(
        description="Lifecycle status. Terminal states: succeeded, failed, cancelled, expired. "
        "One of: pending, queued, processing, succeeded, failed, cancelled, expired."
    )
    model: str
    task_kind: str
    input: dict[str, Any] = Field(description="The normalized request input the task was created with.")
    output: dict[str, Any] | None = Field(
        default=None,
        description="Result payload, present once status=succeeded. Contains hosted asset URLs.",
    )
    error: Seedance20SpicyTextToVideoError | None = None
    estimated_credits_cost: int = Field(
        description="Credits charged up-front when the task was created (1000 credits = $1)."
    )
    actual_credits_cost: int | None = Field(
        default=None, description="Final credits charged after settlement (equals estimate today)."
    )
    webhook_url: str | None = None
    api_key_id: str | None = None
    created_at: int = Field(description="Unix seconds.")
    queued_at: int | None = Field(default=None, description="Unix seconds.")
    started_at: int | None = Field(default=None, description="Unix seconds.")
    completed_at: int | None = Field(default=None, description="Unix seconds.")
    expires_at: int = Field(description="Unix seconds; result and asset retention deadline.")
    reference_video_seconds: float | None = None


class Seedance20SpicyTextToVideoResult(ToolResult):
    data: Seedance20SpicyTextToVideoData | None = None
