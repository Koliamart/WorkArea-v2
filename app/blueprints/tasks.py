from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from extensions import db
from control_db import User, Task


bp = Blueprint('tasks', __name__)

# Создание задачи
@bp.route('/create_task', methods=['GET', 'POST'])  
def create_task():
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')  # Вывод сообщения об ошибке
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    current_user = User.query.get(session['user_id'])  # Получение пользователя по ID
    all_users = User.query.all()  # Получение всех пользователей

    if request.method == 'POST':  # Если метод запроса POST
        try:
            executor_input = request.form.get('executor_id')  # Получение ID исполнителя из формы
            executor_name = executor_input.split(' (')[0].strip()  # Получение имени исполнителя из формы
            executor = User.query.filter_by(user_name=executor_name).first()  # Поиск исполнителя по имени

            if not executor:  # Если исполнитель не найден
                flash('Исполнитель не найден', 'error')  # Вывод сообщения об ошибке
                return redirect(url_for('tasks.create_task'))  # Перенаправление на страницу создания задачи

            term_str = request.form.get('term')  # Получение даты из формы
            term = datetime.strptime(term_str, '%Y-%m-%d').date()  # Преобразование даты в объект datetime

            new_task = Task(
                task_name=request.form['task_name'],  # Получение названия задачи из формы
                description=request.form['description'],  # Получение описания задачи из формы
                creator_id=current_user.id,  # Получение ID создателя задачи
                executor_id=executor.id,  # Получение ID исполнителя задачи
                priority=request.form['priority'],  # Получение приоритета задачи из формы
                term=term,  # Установка даты выполнения задачи
                status='new'  # Установка статуса задачи
            )

            db.session.add(new_task)  # Добавление задачи в базу данных
            db.session.commit()  # Сохранение изменений в базе данных

            flash(f'Задача "{new_task.task_name}" успешно создана', 'success')
            return redirect(url_for('tasks.tasks'))  # Перенаправление на страницу задач

        except SQLAlchemyError as e:
            db.session.rollback()  # Откат транзакции в случае ошибки
            flash(f'Ошибка базы данных: {str(e)}', 'error')  # Вывод сообщения об ошибке
            from flask import current_app
            current_app.logger.error(f'Database error creating task: {str(e)}')  # Логирование ошибки
        except ValueError as e:
            flash('Некорректный формат даты', 'error')  # Вывод сообщения об ошибке
            from flask import current_app
            current_app.logger.error(f'Date format error: {str(e)}')  # Логирование ошибки
        except Exception as e:
            flash('Ошибка при создании задачи', 'error')  # Вывод сообщения об ошибке
            from flask import current_app
            current_app.logger.error(f'Error creating task: {str(e)}')  # Логирование ошибки

    return render_template('create_task.html', task={}, all_users=all_users, current_date=datetime.now().date().isoformat())

# Список задач
@bp.route('/tasks')
def tasks():
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')  # Вывод сообщения об ошибке
        return redirect(url_for('auth.index'))  # Перенаправление на страницу входа

    status_filter = request.args.get('status')  # Получение статуса из запроса
    priority_filter = request.args.get('priority')  # Получение приоритета из запроса
    my_tasks_filter = request.args.get('my_tasks') == 'on'  # Получение фильтра "мои задачи" из запроса

    query = Task.query  # Получение всех задач

    if status_filter:  # Если статус фильтра установлен
        query = query.filter(Task.status == status_filter)  # Фильтрация задач по статусу

    if priority_filter:  # Если приоритет фильтра установлен
        query = query.filter(Task.priority == priority_filter)  # Фильтрация задач по приоритету

    if my_tasks_filter:  # Если фильтр "мои задачи" установлен
        current_user_id = session['user_id']  # Получение ID текущего пользователя
        query = query.filter((Task.creator_id == current_user_id) | (Task.executor_id == current_user_id))  # Фильтрация задач по создателю или исполнителю

    tasks_list = query.order_by(Task.term.asc()).all()  # Получение всех задач, отсортированных по дате выполнения

    return render_template('tasks.html', tasks=tasks_list)  # Рендеринг страницы задач


@bp.route('/task/<int:task_id>')
def task_detail(task_id):   
    if 'user_id' not in session:  # Проверка наличия ID пользователя в сессии
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('auth.index'))

    task = Task.query.get_or_404(task_id)  # Получение задачи по ID
    current_user = User.query.get(session['user_id'])  # Получение пользователя по ID

    return render_template('task_detail.html', task=task, current_user=current_user)  # Рендеринг страницы деталей задачи


@bp.route('/task/<int:task_id>/update_status', methods=['POST'])
def update_task_status(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401  # Возвращение ошибки авторизации

    task = Task.query.get_or_404(task_id)  # Получение задачи по ID
    current_user = User.query.get(session['user_id'])  # Получение пользователя по ID

    if current_user.id != task.executor_id:  # Проверка, является ли пользователь исполнителем задачи
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()  # Получение данных из запроса
    new_status = data.get('status')  # Получение статуса из данных

    if new_status not in ['in_progress', 'done']:  # Проверка, является ли статус допустимым
        return jsonify({'error': 'Invalid status'}), 400

    if (task.status == 'new' and new_status == 'in_progress') or (task.status == 'in_progress' and new_status == 'done'):  # Проверка, является ли переход статусов допустимым
        task.status = new_status  # Установка нового статуса
        db.session.commit()

        if new_status == 'in_progress':
            flash(f'Задача "{task.task_name}" принята в работу', 'success')
        elif new_status == 'done':
            flash(f'Задача "{task.task_name}" выполнена! 🎉', 'success')

        return jsonify({'success': True})  # Возвращение успешного результата
    else:
        return jsonify({'error': 'Invalid status transition'}), 400










