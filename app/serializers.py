from control_db import Task, User


def user_to_public(user: User) -> dict:
    data = {
        'id': user.id,
        'user_name': user.user_name,
        'job_title': user.job_title,
    }
    if user.user_info:
        data['user_info'] = user.user_info
    return data


def user_to_response(user: User) -> dict:
    data = user_to_public(user)
    return data


def task_to_created_event(task: Task) -> dict:
    created = task.created_at
    if created is not None:
        created_at = created.isoformat()
        if created_at.endswith('+00:00'):
            created_at = created_at[:-6] + 'Z'
        elif '+' not in created_at and not created_at.endswith('Z'):
            created_at += 'Z'
    else:
        created_at = ''

    return {
        'id': task.id,
        'task_name': task.task_name,
        'priority': task.priority,
        'term': task.term.isoformat(),
        'creator_id': task.creator_id,
        'executor_id': task.executor_id,
        'creator_name': task.creator.user_name,
        'executor_name': task.executor.user_name,
        'created_at': created_at,
    }


def task_to_response(task: Task) -> dict:
    created = task.created_at
    if created is not None:
        created_at = created.isoformat()
        if created_at.endswith('+00:00'):
            created_at = created_at[:-6] + 'Z'
        elif '+' not in created_at and not created_at.endswith('Z'):
            created_at += 'Z'
    else:
        created_at = ''

    return {
        'id': task.id,
        'task_name': task.task_name,
        'description': task.description or '',
        'status': task.status,
        'priority': task.priority,
        'term': task.term.isoformat(),
        'created_at': created_at,
        'creator': user_to_public(task.creator),
        'executor': user_to_public(task.executor),
    }
