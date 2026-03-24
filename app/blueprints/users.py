from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename # для безопастного имени файла
from extensions import db
from control_db import User
from app.utils.validators import Validators

bp = Blueprint('users', __name__)


@bp.route('/my_page')
def my_page():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    user = User.query.get(session['user_id'])  # Получение пользователя по ID
    return render_template('my_page.html', user=user)  # Рендеринг страницы пользователя


@bp.route('/user_profile/<int:user_id>')
def user_profile(user_id):
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    user = User.query.get(user_id)  # Получение пользователя по ID
    if not user:  # Если пользователь не найден
        flash('Пользователь не найден', 'error')  # Вывод сообщения об ошибке
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    is_my_profile = (session['user_id'] == user_id)  # Проверка, является ли профиль моим
    return render_template('user_profile.html', user=user,
                           is_my_profile=is_my_profile)  # Рендеринг страницы профиля пользователя


@bp.route('/my_profile')
def my_profile():
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')  # Вывод сообщения об ошибке
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    return redirect(
        url_for('users.user_profile', user_id=session['user_id']))  # Перенаправление на страницу профиля пользователя


@bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')  # Вывод сообщения об ошибке
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    user = User.query.get(session['user_id'])  # Получение пользователя по ID

    try:
        user.user_name = request.form.get('user_name', user.user_name)  # Получение имени пользователя из формы
        user.job_title = request.form.get('job_title', user.job_title)  # Получение должности пользователя из формы
        user.user_info = request.form.get('user_info', user.user_info)  # Получение информации о пользователе из формы

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']  # Получение файла из формы

            if file.filename != '':  # Если файл не пустой
                if file.content_type not in ['image/jpeg', 'image/png',
                                             'image/gif']:  # Проверка, является ли файл изображением
                    flash('Разрешены только изображения (JPEG, PNG, GIF)', 'error')  # Вывод сообщения об ошибке
                    return redirect(url_for('users.my_page'))  # Перенаправление на страницу пользователя

                file.seek(0, 2)  # Перемещение файла в конец
                file_size = file.tell()  # Получение размера файла
                file.seek(0)  # Перемещение файла в начало

                if file_size > 2 * 1024 * 1024:  # Проверка, не превышает ли размер файла 2MB
                    flash('Размер файла не должен превышать 2MB', 'error')
                    return redirect(url_for('users.my_page'))  # Перенаправление на страницу пользователя

                user.profile_picture = None  # Установка профиля в None
                user.picture_filename = None  # Установка имени файла в None
                db.session.flush()  # Сохранение изменений в базе данных

                user.profile_picture = file.read()  # Чтение файла
                user.picture_filename = secure_filename(file.filename)  # Получение имени файла

        db.session.commit()  # Сохранение изменений в базе данных
        flash('Профиль успешно обновлен!', 'success')  # Вывод сообщения об успешном обновлении профиля

    except Exception as e:
        db.session.rollback()  # Откат транзакции в случае ошибки
        from flask import current_app
        current_app.logger.error(f'Error updating profile: {str(e)}')  # Логирование ошибки

    return redirect(url_for('users.my_profile'))  # Перенаправление на страницу профиля пользователя


@bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')  # Вывод сообщения об ошибке
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    user = User.query.get(session['user_id'])  # Получение пользователя по ID

    if request.method == 'POST':
        current_password = request.form.get('current_password')  # Получение текущего пароля из формы
        new_password = request.form.get('new_password')  # Получение нового пароля из формы
        confirm_password = request.form.get('confirm_password')  # Получение подтверждения пароля из формы

        if not user.check_password(current_password):  # Проверка, совпадает ли текущий пароль
            flash('Текущий пароль введен неверно', 'error')
            return redirect(url_for('users.change_password'))  # Перенаправление на страницу изменения пароля

        if new_password != confirm_password:  # Проверка, совпадают ли новые пароли
            flash('Новые пароли не совпадают', 'error')
            return redirect(url_for('users.change_password'))  # Перенаправление на страницу изменения пароля

        if user.check_password(new_password):  # Проверка, совпадает ли новый пароль с текущим
            flash('Новый пароль должен отличаться от текущего', 'error')
            return redirect(url_for('users.change_password'))  # Перенаправление на страницу изменения пароля

        if len(new_password) < 8:  # Проверка, не меньше ли длина нового пароля 8 символов
            flash('Пароль должен содержать минимум 8 символов', 'error')
            return redirect(url_for('users.change_password'))

        if not Validators.validate_password(new_password):
            flash('В пароле должна быть хотя бы одна цифра и латинская буква!', 'error')
            return redirect(url_for('users.change_password'))

        try:
            user.set_password(new_password)  # Установка нового пароля
            db.session.commit()  # Сохранение изменений в базе данных
            flash('Пароль успешно изменен!', 'success')  # Вывод сообщения об успешном изменении пароля
            return redirect(url_for('users.my_page'))  # Перенаправление на страницу пользователя
        except Exception as e:
            db.session.rollback()  # Откат транзакции в случае ошибки
            flash('Ошибка при изменении пароля', 'error')  # Вывод сообщения об ошибке
            from flask import current_app
            current_app.logger.error(f'Error changing password: {str(e)}')  # Логирование ошибки
            return redirect(url_for('users.change_password'))  # Перенаправление на страницу изменения пароля

    return render_template('change_password.html')  # Рендеринг страницы изменения пароля






