from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.validators import Validators
from control_db import User


bp = Blueprint('auth', __name__)  # Регистрация блюпринта


@bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:  # Если пользователь уже вошел в систему
        return redirect(url_for('users.my_page'))  # Перенаправление на страницу пользователя
    return render_template('index.html')   # Рендеринг страницы входа


@bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        login_value = request.form.get('login')  # Получение логина из формы
        password = request.form.get('password')  # Получение пароля из формы

        user = User.query.filter_by(login=login_value).first()  # Поиск пользователя по логину

        if user and user.check_password(password):  # Проверка пароля
            session['user_id'] = user.id  # Сохранение ID пользователя в сессии
            return redirect(url_for('auth.hello_win'))  # Перенаправление на страницу приветствия
        else:
            flash('Неверный логин или пароль', 'error')  # Вывод сообщения об ошибке
            return redirect(url_for('auth.index'))  # Перенаправление на страницу входа


@bp.route('/registr', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':  # Если метод запроса POST
        user_name = request.form.get('user_name')  # Получение имени пользователя из формы
        job_title = request.form.get('job_title')  # Получение должности пользователя из формы
        login_value = request.form.get('login')  # Получение логина пользователя из формы
        password = request.form.get('password')  # Получение пароля пользователя из формы
        confirm_password = request.form.get('confirm_password')  # Получение подтверждения пароля пользователя из формы

        if password != confirm_password:  # Проверка совпадения паролей
            flash('Пароли не совпадают!', 'error')  # Вывод сообщения об ошибке
            return redirect(url_for('auth.registration'))  # Перенаправление на страницу регистрации

        if User.query.filter_by(login=login_value).first():  # Проверка существования пользователя с таким логином
            flash('Пользователь с таким логином уже существует!', 'error')  # Вывод сообщения об ошибке
            return redirect(url_for('auth.registration'))  # Перенаправление на страницу регистрации

        if len(password) < 8:  # Проверка длины пароля
            flash('Пароль должен содержать минимум 8 символов', 'error')  # Вывод сообщения об ошибке
            return redirect(url_for('auth.registration'))  # Перенаправление на страницу регистрации

        if not Validators.validate_password(password):  # Проверка пароля на соответствие шаблону
            flash('В пароле должна быть хотя бы одна цифра и латинская буква!', 'error')  # Вывод сообщения об ошибке
            return redirect(url_for('auth.registration'))  # Перенаправление на страницу регистрации

        new_user = User(
            user_name=user_name,
            job_title=job_title,
            login=login_value,
            user_info=""
        )
        new_user.set_password(password)  # Установка пароля

        from extensions import db
        db.session.add(new_user)  # Добавление пользователя в базу данных
        db.session.commit()  # Сохранение изменений в базе данных

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')  # Вывод сообщения об успешной регистрации
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    return render_template('registration.html')  # Рендеринг страницы регистрации


@bp.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаление ID пользователя из сессии
    flash('Вы успешно вышли из системы', 'success')  # Вывод сообщения об успешном выходе
    return redirect(url_for('auth.index'))  # Перенаправление на страницу входа


@bp.route('/hello_win')
def hello_win():
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')  # Вывод сообщения об ошибке
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    user = User.query.get(session['user_id'])  # Получение пользователя по ID
    return render_template('hello_win.html', user=user)  # Рендеринг страницы приветствия









