from flask import Blueprint, g
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.helpers import parse_json, parse_query
from control_db import User
from extensions import db
from app.api.responses import client_error, server_error, validation_error_response
from app.auth.jwt import jwt_required
from app.schemas.task import CreateTaskRequest, PatchTaskRequest, Task, TaskListQuery, TaskListResponse
from app.serializers import task_to_response
from app.services import task_service
from app.services.task_service import TaskError
from control_db import Task as TaskModel

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.get('')
@jwt_required
def list_tasks():
    try:
        query_params = parse_query(TaskListQuery)
    except ValidationError as exc:
        return validation_error_response(exc)

    tasks, total = task_service.list_tasks_for_user(g.current_user, query_params)

    items = [Task.model_validate(task_to_response(task)) for task in tasks]
    response = TaskListResponse(
        items=items,
        total=total,
        limit=query_params.limit,
        offset=query_params.offset,
    )
    return response.model_dump(), 200


@bp.post('')
@jwt_required
def create_task():
    try:
        body = parse_json(CreateTaskRequest)
    except ValidationError as exc:
        return validation_error_response(exc)

    try:
        task = task_service.create_task(g.current_user, body)
    except TaskError as exc:
        return client_error(exc.message, exc.code)

    return Task.model_validate(task_to_response(task)).model_dump(), 201


@bp.get('/<int:task_id>')
@jwt_required
def get_task(task_id: int):
    task = task_service.get_task(task_id)
    if task is None:
        return client_error('Задача не найдена', 404)

    return Task.model_validate(task_to_response(task)).model_dump(), 200


@bp.put('/<int:task_id>')
@jwt_required
def replace_task(task_id: int):
    task = task_service.get_task(task_id)
    if task is None:
        return client_error('Задача не найдена', 404)

    try:
        body = parse_json(CreateTaskRequest)
    except ValidationError as exc:
        return validation_error_response(exc)

    if User.query.get(body.executor_id) is None:
        return client_error('Исполнитель не найден', 400)

    task.task_name = body.task_name
    task.description = body.description or ''
    task.priority = body.priority.value
    task.term = body.term
    task.executor_id = body.executor_id

    try:
        db.session.commit()
        db.session.refresh(task)
    except SQLAlchemyError:
        db.session.rollback()
        return server_error()

    return Task.model_validate(task_to_response(task)).model_dump(), 200


@bp.patch('/<int:task_id>')
@jwt_required
def patch_task(task_id: int):
    task = task_service.get_task(task_id)
    if task is None:
        return client_error('Задача не найдена', 404)

    try:
        body = parse_json(PatchTaskRequest)
    except ValidationError as exc:
        return validation_error_response(exc)

    try:
        task = task_service.apply_patch(task, g.current_user, body)
    except TaskError as exc:
        return client_error(exc.message, exc.code)

    return Task.model_validate(task_to_response(task)).model_dump(), 200


@bp.delete('/<int:task_id>')
@jwt_required
def delete_task(task_id: int):
    task = task_service.get_task(task_id)
    if task is None:
        return client_error('Задача не найдена', 404)

    try:
        db.session.delete(task)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return server_error()

    return '', 204
