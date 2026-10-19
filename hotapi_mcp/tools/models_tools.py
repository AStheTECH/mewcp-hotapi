"""Models group: list_models."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.models import ModelListData, ModelListResult
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("hotapi-mcp.tools.models")


def register_models_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_models",
        description=(
            "Lists the available models with their capabilities, output modality and credit pricing "
            "(1000 credits = $1; pricing shape varies by modality). "
            "Each entry's `id` is the model name to pass as `model` when creating a task."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_models() -> ModelListResult:
        tlog = ToolLogger(logger, "list_models")
        try:
            data, status, retry_after = service.api_request(
                "GET", "/models", timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ModelListResult(success=True, statusCode=status, data=ModelListData(**data))
            return _upstream_err(ModelListResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ModelListResult, tlog, exc)
