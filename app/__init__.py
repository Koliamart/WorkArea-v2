import os
from flask import Flask
from extensions import db, bcrypt
from config import Config
from .utils.filters import b64encode_filter


def create_app(config_object: type[Config] = Config) -> Flask: # Создание приложения
    app = Flask(__name__, template_folder=os.path.abspath('templates'))  # Путь к шаблонам
    app.config.from_object(config_object) # Настройки из config.py
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Ограничение на размер загружаемых файлов для фоток

    db.init_app(app) # Инициализация расширений
    bcrypt.init_app(app) # Инициализация расширений

    from .blueprints.auth import bp as auth_bp 
    from .blueprints.users import bp as users_bp
    from .blueprints.tasks import bp as tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)

    app.add_template_filter(b64encode_filter, name='b64encode') # Добавление фильтра для кодирования base64

    return app









