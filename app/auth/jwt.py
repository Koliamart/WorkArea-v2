from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, request

from control_db import User


def create_access_token(user_id: int) -> tuple[str, int]:
    expires_in = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token, expires_in


def decode_access_token(token: str) -> int:
    payload = jwt.decode(
        token,
        current_app.config['SECRET_KEY'],
        algorithms=['HS256'],
    )
    sub = payload.get('sub')
    if sub is None:
        raise jwt.InvalidTokenError('Отсутствует идентификатор пользователя')
    return int(sub)


def jwt_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        from app.api.responses import client_error

        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return client_error('Не авторизован', 401)

        token = header[7:].strip()
        if not token:
            return client_error('Не авторизован', 401)

        try:
            user_id = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return client_error('Срок действия токена истёк', 401)
        except jwt.InvalidTokenError:
            return client_error('Недействительный токен', 401)

        user = User.query.get(user_id)
        if user is None:
            return client_error('Пользователь не найден', 401)

        g.current_user = user
        return view(*args, **kwargs)

    return wrapper
