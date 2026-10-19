from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class UsageEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    date: str | None = Field(default=None, description="Calendar day (YYYY-MM-DD).")
    model: str | None = None
    request_count: int | None = None
    credits_charged: int | None = Field(default=None, description="Credits charged that day for this model.")
    error_count: int | None = None


class UsageData(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: list[UsageEntry] | None = None


class UsageResult(ToolResult):
    data: UsageData | None = None
