"""Tasks group: cancel_task, create_task, get_task, list_tasks."""

import logging
from urllib.parse import quote

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT, POLL_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas.tasks import (
    CancelTaskData, CancelTaskResult,
    CreateTaskData, CreateTaskResult,
    GetTaskData, GetTaskResult,
    ListTasksData, ListTasksResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("hotapi-mcp.tools.tasks")


def register_tasks_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="cancel_task",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Cancels a generation task by id and returns its id and resulting status. "
            "Cancellation cannot be undone, and the task's output is never produced. "
            "The full estimated charge is refunded only if the task has not started (started_at is null); "
            "once it is processing the provider has been billed and there is no refund. "
            "A task already in a terminal status (succeeded, failed, cancelled, expired) returns a 409 conflict. "
            "NEVER call this tool autonomously or as part of an automated flow. "
            "You MUST stop, tell the user exactly which task will be cancelled and the refund rules above, "
            "and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def cancel_task(
        id: str = Field(description="Task id, from create_task, list_tasks or a per-model generation tool."),
    ) -> CancelTaskResult:
        tlog = ToolLogger(logger, "cancel_task")

        if not id or not id.strip():
            return _err(CancelTaskResult, tlog, "VALIDATION_ERROR", "id must not be empty", 400)

        try:
            data, status, retry_after = service.api_request(
                "DELETE", f"/tasks/{quote(id.strip(), safe='')}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return CancelTaskResult(success=True, statusCode=status, data=CancelTaskData(**data))
            return _upstream_err(CancelTaskResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CancelTaskResult, tlog, exc)

    @mcp.tool(
        name="create_task",
        description=(
            "Submits an asynchronous image or video generation task for any model by model name and a model-specific input object, "
            "and returns the queued task (status queued) to poll with get_task until a terminal status. "
            "Prefer the per-model generation tool when one exists, for example generate_z_image_spicy. "
            "Model names come from list_models. "
            "Credits are charged up-front. "
            "Pass idempotency_key_header to dedupe retries: replaying the same key and body returns the original task, "
            "while the same key with a different request returns a 409 conflict. "
            "Leave webhook and webhook_url unset; results are retrieved by polling get_task."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_task(
        model: str = Field(description="Model name, from list_models (data[].id)."),
        input: dict = Field(description="Model-specific input object. See the per-model generation tool (e.g. generate_z_image_spicy) for the exact fields. For image-input models, images must be public HTTPS URLs."),
        webhook: str | None = Field(default=None, description="Public HTTPS callback URL for the signed terminal task event, sent as a query param. Private addresses and redirects are not supported. Keep unset; results are retrieved by polling get_task."),
        idempotency_key_header: str | None = Field(default=None, description="Stable key for one logical submission, sent as the Idempotency-Key header. Reuse it only when retrying the identical model and input. Omit to send no header."),
        webhook_url: str | None = Field(default=None, description="HTTPS URL for the signed terminal-status callback, sent in the body. Prefer the webhook param. Keep unset; results are retrieved by polling get_task."),
        idempotency_key: str | None = Field(default=None, description="Dedupe key sent in the body. Prefer idempotency_key_header."),
    ) -> CreateTaskResult:
        tlog = ToolLogger(logger, "create_task")

        if not model or not model.strip():
            return _err(CreateTaskResult, tlog, "VALIDATION_ERROR", "model must not be empty", 400)
        if not isinstance(input, dict):
            return _err(CreateTaskResult, tlog, "VALIDATION_ERROR", "input must be an object", 400)

        body: dict = {"model": model.strip(), "input": input}
        if webhook_url is not None:
            body["webhook_url"] = webhook_url
        if idempotency_key is not None:
            body["idempotency_key"] = idempotency_key
        params = {"webhook": webhook} if webhook is not None else None
        headers = {"Idempotency-Key": idempotency_key_header} if idempotency_key_header else None

        try:
            data, status, retry_after = service.api_request(
                "POST", "/tasks", body=body, params=params, headers=headers,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return CreateTaskResult(success=True, statusCode=status, data=CreateTaskData(**data))
            return _upstream_err(CreateTaskResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CreateTaskResult, tlog, exc)

    @mcp.tool(
        name="get_task",
        description=(
            "Fetches a task by id and returns its status, credit costs, timestamps and, once status is succeeded, its output with hosted asset URLs. "
            "Poll until status is terminal (succeeded, failed, cancelled or expired) and stop on the first terminal status; "
            "use 1-2s intervals for fast models and 5s or more for long videos. "
            "Output assets expire at expires_at, so copy them to your own storage before then."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def get_task(
        id: str = Field(description="Task id, from create_task, list_tasks or a per-model generation tool."),
    ) -> GetTaskResult:
        tlog = ToolLogger(logger, "get_task")

        if not id or not id.strip():
            return _err(GetTaskResult, tlog, "VALIDATION_ERROR", "id must not be empty", 400)

        try:
            data, status, retry_after = service.api_request(
                "GET", f"/tasks/{quote(id.strip(), safe='')}",
                timeout=(CONNECT_TIMEOUT, POLL_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetTaskResult(success=True, statusCode=status, data=GetTaskData(**data))
            return _upstream_err(GetTaskResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetTaskResult, tlog, exc)

    @mcp.tool(
        name="list_tasks",
        description=(
            "Lists the organization's tasks, most recent first, with cursor pagination (max 100 per page), "
            "and returns the page of tasks plus next_cursor. "
            "Filterable by status (or active for everything not yet terminal), API key, free-text query and creation date range. "
            "Use fields=summary when polling to omit input and output, since an inlined image input can be megabytes; "
            "then call get_task for the payload."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True),
    )
    def list_tasks(
        limit: int | None = Field(default=None, description="Max results per page, 1-100. Omit for the API default of 20."),
        cursor: str | None = Field(default=None, description="Pagination cursor from a prior next_cursor. Omit for the first page."),
        status: str | None = Field(default=None, description="Filter by lifecycle status (pending, queued, processing, succeeded, failed, cancelled, expired), or active for everything not yet terminal (pending, queued, processing). Omit for all."),
        q: str | None = Field(default=None, description="Free-text search over task id, model and task kind."),
        fields: str | None = Field(default=None, description="full (default) includes input and output; summary omits both. Prefer summary when polling a list."),
        api_key_id: str | None = Field(default=None, description="Only tasks created by this API key of the organization."),
        created_after: str | None = Field(default=None, description="ISO 8601 timestamp. Only tasks created at or after this instant."),
        created_before: str | None = Field(default=None, description="ISO 8601 timestamp (exclusive). Only tasks created before this instant."),
    ) -> ListTasksResult:
        tlog = ToolLogger(logger, "list_tasks")

        if limit is not None and (limit < 1 or limit > 100):
            return _err(ListTasksResult, tlog, "VALIDATION_ERROR", "limit must be 1-100", 400)
        if fields is not None and fields not in ("full", "summary"):
            return _err(ListTasksResult, tlog, "VALIDATION_ERROR", "fields must be 'full' or 'summary'", 400)

        candidates = {
            "limit": limit, "cursor": cursor, "status": status, "q": q, "fields": fields,
            "api_key_id": api_key_id, "created_after": created_after, "created_before": created_before,
        }
        params = {k: v for k, v in candidates.items() if v is not None}

        try:
            data, status_code, retry_after = service.api_request(
                "GET", "/tasks", params=params or None,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status_code < 300:
                tlog.success()
                return ListTasksResult(success=True, statusCode=status_code, data=ListTasksData(**data))
            return _upstream_err(ListTasksResult, tlog, status_code, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListTasksResult, tlog, exc)
