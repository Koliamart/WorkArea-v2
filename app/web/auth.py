from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.auth_service import AuthError, safe_login, safe_register
from app.web.decorators import clear_session, login_required, set_session_user

bp = Blueprint('auth', __name__)


@bp.route('/terms')
def terms():
    return render_template('terms.html')


@bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('auth.hello_win'))

    if request.method == 'POST':
        try:
            user, token, _ = safe_login({
                'login': request.form.get('login', ''),
                'password': request.form.get('password', ''),
            })
            set_session_user(user, token)
            return redirect(url_for('auth.hello_win'))
        except AuthError as exc:
            flash(exc.message, 'error')

    return render_template('index.html')


@bp.route('/login', methods=['POST'])
def login():
    return index()


@bp.route('/registr', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        try:
            safe_register({
                'user_name': request.form.get('user_name', ''),
                'job_title': request.form.get('job_title', ''),
                'login': request.form.get('login', ''),
                'password': request.form.get('password', ''),
                'confirm_password': request.form.get('confirm_password', ''),
            })
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('auth.index'))
        except AuthError as exc:
            flash(exc.message, 'error')
            return redirect(url_for('auth.registration'))

    return render_template('registration.html')


@bp.route('/logout')
def logout():
    clear_session()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth.index'))


@bp.route('/hello_win')
@login_required
def hello_win():
    from app.web.decorators import get_current_user

    user = get_current_user()
    return render_template('hello_win.html', user=user)
