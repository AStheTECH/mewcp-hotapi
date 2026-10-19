from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = Field(default=None, description="The model name to pass as `model` when creating a task.")
    object: str | None = None
    created: int | None = Field(default=None, description="Unix seconds.")
    owned_by: str | None = None
    modal: str | None = Field(default=None, description="Output modality.")
    task_kind: str | None = None
    description: str | None = None
    capabilities: list[str] | None = None
    pricing: dict[str, Any] | None = Field(
        default=None,
        description="Credit pricing (1000 credits = $1). Shape varies by modality.",
    )


class ModelListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    object: str | None = None
    data: list[ModelInfo] | None = None


class ModelListResult(ToolResult):
    data: ModelListData | None = None
