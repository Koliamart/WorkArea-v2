import os
from dotenv import load_dotenv

# Корень проекта: каталог, где лежит этот файл (независимо от cwd под Passenger/WSGI)
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Переменные из .env в корне проекта
load_dotenv(os.path.join(_PROJECT_ROOT, '.env'))


class Config:
    # Безопасность
    SECRET_KEY = os.environ.get('SECRET_KEY') # Секретный ключ для шифрования

    if not SECRET_KEY:
        raise ValueError('SECRET_KEY не задан!')

    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///work_area.db'  # URI для базы данных

    # Логи (см. app/logging_config.py): LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
    # LOG_FILE не задан — logs/app.log; LOG_FILE= — только stderr; иначе путь к файлу
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Отключение отслеживания изменений

    # JWT (OpenAPI bearerAuth)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_EXPIRES_IN', 3600))
