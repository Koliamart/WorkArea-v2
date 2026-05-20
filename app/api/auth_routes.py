from flask import Blueprint
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.helpers import parse_json
from app.api.responses import client_error, server_error, validation_error_response
from app.auth.jwt import jwt_required
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    Registration,
    RegistrationSuccess,
)
from app.services.auth_service import AuthError, authenticate, change_password, register_user
from extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.post('/registr/')
@bp.post('/registr')
def register():
    try:
        body = parse_json(Registration)
    except ValidationError as exc:
        return validation_error_response(exc)

    try:
        register_user(body)
    except AuthError as exc:
        return client_error(exc.message, exc.code)
    except SQLAlchemyError:
        db.session.rollback()
        return server_error()

    return RegistrationSuccess().model_dump(), 201


@bp.post('/login')
def login():
    try:
        body = parse_json(LoginRequest)
    except ValidationError as exc:
        return validation_error_response(exc)

    try:
        user, token, expires_in = authenticate(body)
    except AuthError as exc:
        return client_error(exc.message, exc.code)
    except Exception:
        return server_error()

    response = AuthResponse(access_token=token, expires_in=expires_in)
    return response.model_dump(), 200


@bp.post('/change-password')
@jwt_required
def change_password():
    from flask import g

    try:
        body = parse_json(ChangePasswordRequest)
    except ValidationError as exc:
        return validation_error_response(exc)

    user = g.current_user

    try:
        change_password(user, body)
    except AuthError as exc:
        return client_error(exc.message, exc.code)
    except SQLAlchemyError:
        db.session.rollback()
        return server_error()

    return '', 200
