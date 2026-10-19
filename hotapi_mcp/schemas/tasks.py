from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class TaskError(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = None
    code: str | None = None
    message: str | None = None


class CancelTaskData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    status: str | None = None


class CancelTaskResult(ToolResult):
    data: CancelTaskData | None = None


class CreateTaskData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    object: str
    status: str = Field(description="Lifecycle status: pending, queued, processing, succeeded, failed, cancelled or expired. Terminal states: succeeded, failed, cancelled, expired.")
    model: str
    task_kind: str
    input: dict = Field(description="The normalized request input the task was created with.")
    output: dict | None = Field(default=None, description="Result payload, present once status=succeeded. Contains hosted asset URLs.")
    error: TaskError | None = None
    estimated_credits_cost: int = Field(description="Credits charged up-front when the task was created (1000 credits = $1).")
    actual_credits_cost: int | None = Field(default=None, description="Final credits charged after settlement (equals estimate today).")
    webhook_url: str | None = None
    api_key_id: str | None = Field(default=None, description="The organization's API key that created the task; absent for dashboard/session-created tasks.")
    created_at: int = Field(description="Unix seconds.")
    queued_at: int | None = Field(default=None, description="Unix seconds.")
    started_at: int | None = Field(default=None, description="Unix seconds.")
    completed_at: int | None = Field(default=None, description="Unix seconds.")
    expires_at: int = Field(description="Unix seconds; result and asset retention deadline.")
    reference_video_seconds: float | None = Field(default=None, description="Input-video seconds measured and frozen at submission. Zero when no reference video was supplied.")


class CreateTaskResult(ToolResult):
    data: CreateTaskData | None = None


class GetTaskData(CreateTaskData):
    pass


class GetTaskResult(ToolResult):
    data: GetTaskData | None = None


class TaskListItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    object: str | None = None
    status: str | None = Field(default=None, description="Lifecycle status, e.g. queued.")
    model: str | None = None
    task_kind: str | None = None
    input: dict | None = Field(default=None, description="Omitted when fields=summary.")
    output: dict | None = Field(default=None, description="Omitted when fields=summary.")
    error: TaskError | None = None
    estimated_credits_cost: int | None = None
    actual_credits_cost: int | None = None
    webhook_url: str | None = None
    api_key_id: str | None = None
    created_at: int | None = None
    queued_at: int | None = None
    started_at: int | None = None
    completed_at: int | None = None
    expires_at: int | None = None


class ListTasksData(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: list[TaskListItem] | None = Field(default=None, description="The tasks on this page, most recent first.")
    next_cursor: str | None = Field(default=None, description="Pass as cursor to get the next page.")


class ListTasksResult(ToolResult):
    data: ListTasksData | None = None
