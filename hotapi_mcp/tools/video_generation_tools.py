"""Video generation group: generate_seedance_2_0_spicy_text_to_video"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.video_generation import (
    Seedance20SpicyTextToVideoData,
    Seedance20SpicyTextToVideoResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("hotapi-mcp.tools.video_generation")

_RESOLUTIONS = ("480p", "720p", "1080p")
_RATIOS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16", "adaptive")


def register_video_generation_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="generate_seedance_2_0_spicy_text_to_video",
        description=(
            "Submits an asynchronous, uncensored text-to-video task on the seedance-2.0-spicy model "
            "(480p/720p/1080p, 4-15s, selectable aspect ratio, optional synced audio) and returns the "
            "queued task, including its id and estimated credit cost. Poll the task with get_task at "
            "5-second intervals or longer until it reaches a terminal status; the video URL appears in "
            "`output` once status is succeeded. If the generated audio is rejected by provider "
            "moderation the whole task fails with no video and a full refund; pass generate_audio=false "
            "for a silent video to avoid this."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def generate_seedance_2_0_spicy_text_to_video(
        prompt: str = Field(description="Text prompt describing the video to generate."),
        duration_seconds: int = Field(description="Video length in seconds, 4-15."),
        resolution: str | None = Field(
            default=None,
            description="Output resolution: 480p, 720p or 1080p. Omit for the cheapest tier (480p).",
        ),
        ratio: str | None = Field(
            default=None,
            description="Output aspect ratio: 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 or adaptive. "
            "Omit and the model chooses from your prompt (adaptive).",
        ),
        generate_audio: bool = Field(
            default=True,
            description="Generate a synced audio track. If audio is rejected by provider moderation the "
            "whole task fails (fully refunded); pass false for a silent video to avoid this.",
        ),
        seed: int | None = Field(
            default=None,
            description="Random seed, 0-2147483647. Omit for a random seed.",
        ),
        webhook: str | None = Field(
            default=None,
            description="Public HTTPS callback URL for the signed terminal task event. "
            "Leave unset; retrieve results by polling get_task.",
        ),
        idempotency_key: str | None = Field(
            default=None,
            description="Stable key for one logical submission, sent as the Idempotency-Key header. "
            "Reuse it only when retrying the identical model and input.",
        ),
    ) -> Seedance20SpicyTextToVideoResult:
        tlog = ToolLogger(logger, "generate_seedance_2_0_spicy_text_to_video")
        R = Seedance20SpicyTextToVideoResult

        if not prompt or not prompt.strip():
            return _err(R, tlog, "VALIDATION_ERROR", "prompt must not be empty", 400)
        if duration_seconds < 4 or duration_seconds > 15:
            return _err(R, tlog, "VALIDATION_ERROR", "duration_seconds must be 4-15", 400)
        if resolution is not None and resolution not in _RESOLUTIONS:
            return _err(R, tlog, "VALIDATION_ERROR",
                        f"resolution must be one of: {', '.join(_RESOLUTIONS)}", 400)
        if ratio is not None and ratio not in _RATIOS:
            return _err(R, tlog, "VALIDATION_ERROR",
                        f"ratio must be one of: {', '.join(_RATIOS)}", 400)
        if seed is not None and (seed < 0 or seed > 2147483647):
            return _err(R, tlog, "VALIDATION_ERROR", "seed must be 0-2147483647", 400)

        body: dict = {
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "generate_audio": generate_audio,
        }
        if resolution is not None:
            body["resolution"] = resolution
        if ratio is not None:
            body["ratio"] = ratio
        if seed is not None:
            body["seed"] = seed
        params = {"webhook": webhook} if webhook else None
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None

        try:
            data, status, retry_after = service.api_request(
                "POST", "/seedance-2.0-spicy/text-to-video",
                body=body, params=params, headers=headers,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return R(success=True, statusCode=status,
                         data=Seedance20SpicyTextToVideoData(**data))
            return _upstream_err(R, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(R, tlog, exc)
