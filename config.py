import os
from dotenv import load_dotenv


# Переменные из .env
load_dotenv()


class Config:
    # Безопасность
    SECRET_KEY = os.environ.get('SECRET_KEY') # Секретный ключ для шифрования

    if not SECRET_KEY:
        raise ValueError('SECRET_KEY не задан!')

    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///work_area.db'  # URI для базы данных
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Отключение отслеживания изменений
