from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.auth.jwt import create_access_token
from app.schemas.auth import ChangePasswordRequest, LoginRequest, Registration
from control_db import User
from extensions import db


class AuthError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


def register_user(data: Registration) -> User:
    if User.query.filter_by(login=data.login).first():
        raise AuthError('Пользователь с таким логином уже существует', 409)

    user = User(
        user_name=data.user_name,
        job_title=data.job_title,
        login=data.login,
        user_info='',
    )
    user.set_password(data.password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(data: LoginRequest) -> tuple[User, str, int]:
    if not data.login or not data.password:
        raise AuthError('Логин и пароль обязательны', 400)

    user = User.query.filter_by(login=data.login).first()
    if user is None or not user.check_password(data.password):
        raise AuthError('Неверный логин или пароль', 401)

    token, expires_in = create_access_token(user.id)
    return user, token, expires_in


def change_password(user: User, data: ChangePasswordRequest) -> None:
    if not user.check_password(data.current_password):
        raise AuthError('Неверный текущий пароль', 401)

    user.set_password(data.new_password)
    db.session.commit()


def safe_register(raw: dict) -> User:
    try:
        data = Registration.model_validate(raw)
    except ValidationError as exc:
        raise AuthError(_first_validation_message(exc), 400) from exc
    return register_user(data)


def safe_login(raw: dict) -> tuple[User, str, int]:
    try:
        data = LoginRequest.model_validate(raw)
    except ValidationError as exc:
        raise AuthError(_first_validation_message(exc), 400) from exc
    return authenticate(data)


def safe_change_password(user: User, raw: dict) -> None:
    try:
        data = ChangePasswordRequest.model_validate(raw)
    except ValidationError as exc:
        raise AuthError(_first_validation_message(exc), 400) from exc

    try:
        change_password(user, data)
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise AuthError('Ошибка при изменении пароля', 500) from exc


def _first_validation_message(exc: ValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return 'Ошибка валидации'
    return errors[0].get('msg', 'Ошибка валидации')
