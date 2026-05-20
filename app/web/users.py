from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from pydantic import ValidationError

from app.schemas.user import PatchMeProfile
from app.services.auth_service import AuthError, safe_change_password
from app.services.user_service import patch_profile, update_avatar
from app.web.decorators import get_current_user, login_required
from control_db import User
from extensions import db

bp = Blueprint('users', __name__)


@bp.route('/my_page')
@login_required
def my_page():
    user = get_current_user()
    return render_template('my_page.html', user=user)


@bp.route('/user_profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('auth.index'))

    is_my_profile = session['user_id'] == user_id
    return render_template(
        'user_profile.html',
        user=user,
        is_my_profile=is_my_profile,
    )


@bp.route('/my_profile')
@login_required
def my_profile():
    return redirect(url_for('users.user_profile', user_id=session['user_id']))


@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = get_current_user()

    try:
        profile_data = PatchMeProfile(
            user_name=request.form.get('user_name') or None,
            job_title=request.form.get('job_title') or None,
            user_info=request.form.get('user_info'),
        )
        if profile_data.model_fields_set:
            patch_profile(user, profile_data)

        if 'profile_picture' in request.files:
            update_avatar(user, request.files['profile_picture'])

        flash('Профиль успешно обновлен!', 'success')
    except ValidationError as exc:
        flash(exc.errors()[0].get('msg', 'Ошибка валидации'), 'error')
    except ValueError as exc:
        flash(str(exc), 'error')
    except Exception:
        db.session.rollback()
        flash('Ошибка при обновлении профиля', 'error')

    return redirect(url_for('users.my_profile'))


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = get_current_user()

    if request.method == 'POST':
        try:
            safe_change_password(user, {
                'current_password': request.form.get('current_password', ''),
                'new_password': request.form.get('new_password', ''),
                'confirm_password': request.form.get('confirm_password', ''),
            })
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('users.my_page'))
        except AuthError as exc:
            flash(exc.message, 'error')
            return redirect(url_for('users.change_password'))

    return render_template('change_password.html')
