from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from pydantic import ValidationError

from app.schemas.enums import TaskStatus
from app.schemas.task import CreateTaskRequest, TaskListQuery
from app.services import task_service
from app.services.task_service import TaskError, resolve_executor_id
from app.web.decorators import get_current_user, login_required
from control_db import User

bp = Blueprint('tasks', __name__)

_WEB_TASK_LIMIT = 500


@bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    current_user = get_current_user()
    all_users = User.query.order_by(User.user_name).all()

    if request.method == 'POST':
        executor_id = resolve_executor_id(request.form.get('executor_id', ''))
        if executor_id is None:
            flash('Исполнитель не найден', 'error')
            return redirect(url_for('tasks.create_task'))

        try:
            term = datetime.strptime(request.form['term'], '%Y-%m-%d').date()
            body = CreateTaskRequest(
                task_name=request.form['task_name'],
                description=request.form.get('description') or '',
                priority=request.form['priority'],
                term=term,
                executor_id=executor_id,
            )
            task = task_service.create_task(current_user, body)
            flash(f'Задача "{task.task_name}" успешно создана', 'success')
            return redirect(url_for('tasks.tasks'))
        except ValidationError as exc:
            flash(exc.errors()[0].get('msg', 'Ошибка валидации'), 'error')
        except TaskError as exc:
            flash(exc.message, 'error')
        except ValueError:
            flash('Некорректный формат даты', 'error')
        except Exception:
            flash('Ошибка при создании задачи', 'error')

    return render_template(
        'create_task.html',
        task={},
        all_users=all_users,
        current_date=datetime.now().date().isoformat(),
    )


@bp.route('/tasks')
@login_required
def tasks():
    current_user = get_current_user()
    status_raw = request.args.get('status') or None
    priority_raw = request.args.get('priority') or None

    try:
        params = TaskListQuery(
            status=status_raw,
            priority=priority_raw,
            my_task=request.args.get('my_tasks') == 'on',
            limit=_WEB_TASK_LIMIT,
            offset=0,
        )
    except ValidationError:
        flash('Неверные параметры фильтра', 'error')
        params = TaskListQuery(my_task=False, limit=_WEB_TASK_LIMIT, offset=0)

    tasks_list, _ = task_service.list_tasks_for_user(current_user, params)
    return render_template('tasks.html', tasks=tasks_list)


@bp.route('/task/<int:task_id>')
@login_required
def task_detail(task_id):
    task = task_service.get_task(task_id)
    if task is None:
        flash('Задача не найдена', 'error')
        return redirect(url_for('tasks.tasks'))

    current_user = get_current_user()
    return render_template('task_detail.html', task=task, current_user=current_user)
