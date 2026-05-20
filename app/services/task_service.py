from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.enums import TaskStatus
from app.schemas.task import CreateTaskRequest, PatchTaskRequest, TaskListQuery
from control_db import Task, User
from extensions import db

STATUS_TRANSITIONS = {
    (TaskStatus.new, TaskStatus.in_progress),
    (TaskStatus.in_progress, TaskStatus.done),
}


class TaskError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


def list_tasks_for_user(user: User, params: TaskListQuery) -> tuple[list[Task], int]:
    query = Task.query

    if params.status is not None:
        query = query.filter(Task.status == params.status.value)

    if params.priority is not None:
        query = query.filter(Task.priority == params.priority.value)

    if params.my_task:
        query = query.filter(
            or_(Task.creator_id == user.id, Task.executor_id == user.id),
        )

    total = query.count()
    tasks = (
        query.order_by(Task.term.asc())
        .offset(params.offset)
        .limit(params.limit if params.limit > 0 else None)
        .all()
    )
    return tasks, total


def get_task(task_id: int) -> Task | None:
    if task_id < 1:
        return None
    return Task.query.get(task_id)


def create_task(creator: User, data: CreateTaskRequest) -> Task:
    if User.query.get(data.executor_id) is None:
        raise TaskError('Исполнитель не найден', 400)

    task = Task(
        task_name=data.task_name,
        description=data.description or '',
        creator_id=creator.id,
        executor_id=data.executor_id,
        priority=data.priority.value,
        term=data.term,
        status=TaskStatus.new.value,
    )
    db.session.add(task)
    db.session.commit()
    db.session.refresh(task)
    return task


def apply_patch(task: Task, user: User, data: PatchTaskRequest) -> Task:
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise TaskError('Нет полей для обновления', 400)

    if 'status' in updates:
        new_status = updates.pop('status')
        if isinstance(new_status, str):
            new_status = TaskStatus(new_status)
        _apply_status_change(task, user, new_status)

    if 'executor_id' in updates and User.query.get(updates['executor_id']) is None:
        raise TaskError('Исполнитель не найден', 400)

    if 'priority' in updates:
        updates['priority'] = updates['priority'].value

    for field, value in updates.items():
        setattr(task, field, value)

    try:
        db.session.commit()
        db.session.refresh(task)
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise TaskError('Ошибка при сохранении задачи', 500) from exc

    return task


def _apply_status_change(task: Task, user: User, new_status: TaskStatus) -> None:
    if task.executor_id != user.id:
        raise TaskError('Только исполнитель может менять статус задачи', 403)

    try:
        current = TaskStatus(task.status)
    except ValueError as exc:
        raise TaskError('Некорректный текущий статус задачи', 400) from exc

    if (current, new_status) not in STATUS_TRANSITIONS:
        raise TaskError('Недопустимый переход статуса', 400)

    task.status = new_status.value


def resolve_executor_id(executor_input: str) -> int | None:
    if not executor_input:
        return None
    name = executor_input.split(' (')[0].strip()
    user = User.query.filter_by(user_name=name).first()
    return user.id if user else None
