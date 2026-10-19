from pydantic import BaseModel, ConfigDict
from ._base import ToolResult


class FaceAssetItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    source_url: str | None = None
    created_at: str | None = None
    last_used_at: str | None = None


class FaceAssetListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: list[FaceAssetItem] | None = None
    next_cursor: str | None = None
    used: int | float | None = None
    limit: int | float | None = None


class FaceAssetListResult(ToolResult):
    data: FaceAssetListData | None = None
