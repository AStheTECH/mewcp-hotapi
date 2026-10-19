"""Image generation group: generate_z_image_spicy."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.image_generation import ZImageSpicyData, ZImageSpicyResult
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("hotapi-mcp.tools.image_generation")


def register_image_generation_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="generate_z_image_spicy",
        description=(
            "Submits an asynchronous uncensored text-to-image task on the z-image-spicy model and returns "
            "the queued task (id, status, estimated_credits_cost) without waiting for the image. "
            "Credits are charged up-front; poll get_task with the returned id until status is terminal "
            "(succeeded, failed, cancelled, expired) to retrieve the hosted image URLs in `output`. "
            "Leave `webhook` unset and retrieve results by polling."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def generate_z_image_spicy(
        prompt: str = Field(description="Text prompt describing the image to generate."),
        width: int | None = Field(default=None, description="Image width in pixels, 256-1536. Omit to use the model default."),
        height: int | None = Field(default=None, description="Image height in pixels, 256-1536. Omit to use the model default."),
        seed: int | None = Field(default=None, description="Random seed, 0-2147483647. Omit for a random seed."),
        webhook: str | None = Field(
            default=None,
            description="Public HTTPS callback URL for the signed terminal task event (private addresses and redirects are not supported). Leave unset; results are retrieved by polling get_task.",
        ),
        idempotency_key: str | None = Field(
            default=None,
            description="Stable key for one logical submission, sent as the Idempotency-Key header. Reuse it only when retrying the identical model and input. Omit for a new submission.",
        ),
    ) -> ZImageSpicyResult:
        tlog = ToolLogger(logger, "generate_z_image_spicy")

        if not prompt or not prompt.strip():
            return _err(ZImageSpicyResult, tlog, "VALIDATION_ERROR", "prompt must not be empty", 400)
        if width is not None and not 256 <= width <= 1536:
            return _err(ZImageSpicyResult, tlog, "VALIDATION_ERROR", "width must be 256-1536", 400)
        if height is not None and not 256 <= height <= 1536:
            return _err(ZImageSpicyResult, tlog, "VALIDATION_ERROR", "height must be 256-1536", 400)
        if seed is not None and not 0 <= seed <= 2147483647:
            return _err(ZImageSpicyResult, tlog, "VALIDATION_ERROR", "seed must be 0-2147483647", 400)

        body: dict = {"prompt": prompt}
        if width is not None:
            body["width"] = width
        if height is not None:
            body["height"] = height
        if seed is not None:
            body["seed"] = seed
        params = {"webhook": webhook} if webhook else None
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None

        try:
            data, status, retry_after = service.api_request(
                "POST", "/z-image-spicy", body=body, params=params, headers=headers,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return ZImageSpicyResult(success=True, statusCode=status, data=ZImageSpicyData(**data))
            return _upstream_err(ZImageSpicyResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ZImageSpicyResult, tlog, exc)
