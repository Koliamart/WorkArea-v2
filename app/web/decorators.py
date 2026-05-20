from functools import wraps

from flask import flash, redirect, session, url_for

from control_db import User


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('auth.index'))
        return view(*args, **kwargs)

    return wrapper


def get_current_user() -> User | None:
    user_id = session.get('user_id')
    if user_id is None:
        return None
    return User.query.get(user_id)


def set_session_user(user: User, access_token: str) -> None:
    session['user_id'] = user.id
    session['access_token'] = access_token


def clear_session() -> None:
    session.pop('user_id', None)
    session.pop('access_token', None)
