from flask import Blueprint, Response, g
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.helpers import parse_json
from app.api.responses import client_error, server_error, validation_error_response
from app.auth.jwt import jwt_required
from app.schemas.user import PatchMeProfile, User
from app.serializers import user_to_response
from control_db import User as UserModel
from extensions import db

bp = Blueprint('users', __name__, url_prefix='/users')


def _avatar_mimetype(filename: str | None) -> str:
    if not filename:
        return 'image/jpeg'
    ext = filename.rsplit('.', 1)[-1].lower()
    return {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
    }.get(ext, 'image/jpeg')


@bp.get('/me')
@jwt_required
def get_me():
    try:
        return User.model_validate(user_to_response(g.current_user)).model_dump(exclude_none=True), 200
    except ValidationError:
        return server_error()


@bp.patch('/me')
@jwt_required
def patch_me():
    try:
        body = parse_json(PatchMeProfile)
    except ValidationError as exc:
        return validation_error_response(exc)

    if not body.model_fields_set:
        return client_error('Нет полей для обновления', 400)

    user = g.current_user
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return server_error()

    return User.model_validate(user_to_response(user)).model_dump(exclude_none=True), 200


@bp.get('/me/avatar')
@jwt_required
def get_my_avatar():
    user = g.current_user
    if not user.profile_picture:
        return client_error('Аватар не загружен', 404)

    return Response(
        user.profile_picture,
        mimetype=_avatar_mimetype(user.picture_filename),
    )


@bp.get('/<int:id>/avatar')
@jwt_required
def get_user_avatar(id: int):
    user = UserModel.query.get(id)
    if user is None:
        return client_error('Пользователь не найден', 404)

    if not user.profile_picture:
        return client_error('Аватар не загружен', 404)

    return Response(
        user.profile_picture,
        mimetype=_avatar_mimetype(user.picture_filename),
    )
