from datetime import date

from pydantic import BaseModel, Field

from app.schemas.enums import TaskPriority, TaskStatus
from app.schemas.user import UserPublic


class CreateTaskRequest(BaseModel):
    task_name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    priority: TaskPriority
    term: date
    executor_id: int


class PatchTaskRequest(BaseModel):
    task_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    term: date | None = None
    executor_id: int | None = None


class Task(BaseModel):
    id: int
    task_name: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    term: date
    created_at: str
    creator: UserPublic
    executor: UserPublic


class TaskListResponse(BaseModel):
    items: list[Task]
    total: int
    limit: int
    offset: int


class TaskListQuery(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    my_task: bool = False
    limit: int = Field(default=20, ge=0)
    offset: int = Field(default=0, ge=0)
