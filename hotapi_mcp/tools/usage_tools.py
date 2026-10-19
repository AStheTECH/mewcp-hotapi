"""Usage group: get_usage"""

import logging
from datetime import datetime

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.usage import UsageData, UsageResult
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("hotapi-mcp.tools.usage")


def _valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return len(value) == 10
    except ValueError:
        return False


def register_usage_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_usage",
        description=(
            "Retrieves daily usage rollups for the organization, one entry per model per day, most recent first. "
            "Each entry returns the date, model, request count, credits charged and error count. "
            "Optionally restrict to an inclusive date range with `from_date` and `to_date`."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_usage(
        from_date: str | None = Field(default=None, description="Start date YYYY-MM-DD (inclusive). Omit for no lower bound."),
        to_date: str | None = Field(default=None, description="End date YYYY-MM-DD (inclusive). Omit for no upper bound."),
    ) -> UsageResult:
        tlog = ToolLogger(logger, "get_usage")

        if from_date is not None and not _valid_date(from_date):
            return _err(UsageResult, tlog, "VALIDATION_ERROR", "from_date must be in YYYY-MM-DD format", 400)
        if to_date is not None and not _valid_date(to_date):
            return _err(UsageResult, tlog, "VALIDATION_ERROR", "to_date must be in YYYY-MM-DD format", 400)

        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date

        try:
            data, status, retry_after = service.api_request(
                "GET", "/usage", params=params or None,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return UsageResult(success=True, statusCode=status, data=UsageData(**data))
            return _upstream_err(UsageResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(UsageResult, tlog, exc)
