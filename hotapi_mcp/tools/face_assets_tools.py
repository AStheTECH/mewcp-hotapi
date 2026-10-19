"""Face assets group: list_face_assets"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.face_assets import FaceAssetListData, FaceAssetListResult
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("hotapi-mcp.tools.face_assets")


def register_face_assets_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_face_assets",
        description=(
            "Lists the organization's trusted reference faces (images and videos auto-registered with the video provider), "
            "oldest-used first. Returns each face's id, source_url, created_at and last_used_at, plus the `used` and `limit` "
            "quota counts and a `next_cursor` for pagination. Each organization can hold up to 200 faces; at the cap, new "
            "submissions fail with `400 trusted_face_limit_reached` until unused faces are deleted. Use `unused_since` to find "
            "prune candidates; the returned `id` is what delete_face_asset takes."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_face_assets(
        limit: str = Field(default="50", description="Page size as an integer string, 1-200. Defaults to 50."),
        cursor: str | None = Field(default=None, description="Pagination cursor from the previous response's `next_cursor`. Omit for the first page."),
        unused_since: str | None = Field(default=None, description="ISO date; returns only faces last used before this date (prune candidates). Omit to list all faces."),
    ) -> FaceAssetListResult:
        tlog = ToolLogger(logger, "list_face_assets")

        try:
            limit_int = int(limit.strip())
        except (ValueError, AttributeError):
            return _err(FaceAssetListResult, tlog, "VALIDATION_ERROR", "limit must be an integer between 1 and 200", 400)
        if limit_int < 1 or limit_int > 200:
            return _err(FaceAssetListResult, tlog, "VALIDATION_ERROR", "limit must be between 1 and 200", 400)

        params: dict = {"limit": str(limit_int)}
        if cursor is not None:
            params["cursor"] = cursor
        if unused_since is not None:
            params["unused_since"] = unused_since

        try:
            data, status, retry_after = service.api_request(
                "GET", "/face-assets", params=params,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return FaceAssetListResult(success=True, statusCode=status, data=FaceAssetListData(**data))
            return _upstream_err(FaceAssetListResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(FaceAssetListResult, tlog, exc)
