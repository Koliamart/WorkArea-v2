from werkzeug.utils import secure_filename

from app.schemas.user import PatchMeProfile
from control_db import User
from extensions import db

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif'}
MAX_AVATAR_SIZE = 2 * 1024 * 1024


def patch_profile(user: User, data: PatchMeProfile) -> User:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)
    db.session.commit()
    return user


def update_avatar(user: User, file) -> None:
    if not file or not file.filename:
        return

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError('Разрешены только изображения (JPEG, PNG, GIF)')

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_AVATAR_SIZE:
        raise ValueError('Размер файла не должен превышать 2MB')

    user.profile_picture = file.read()
    user.picture_filename = secure_filename(file.filename)
    db.session.commit()
