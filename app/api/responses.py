from flask import jsonify
from pydantic import ValidationError


def client_error(message: str, code: int = 400, details: dict | None = None):
    body = {'code': code, 'message': message}
    if details:
        body['details'] = details
    return jsonify(body), code


def server_error(message: str = 'Внутренняя ошибка сервера'):
    return jsonify({'code': 500, 'message': message}), 500


def validation_error_response(exc: ValidationError):
    errors = exc.errors()
    if not errors:
        return client_error('Ошибка валидации', 400)

    first = errors[0]
    loc = first.get('loc', ())
    field = '.'.join(str(part) for part in loc if part != 'body')
    reason = first.get('msg', 'Некорректное значение')
    return client_error(
        'Ошибка валидации',
        400,
        details={'field': field or None, 'reason': reason},
    )
