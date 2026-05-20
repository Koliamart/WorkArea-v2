import sys
import os

# --- НАСТРОЙТЕ ЭТИ ПЕРЕМЕННЫЕ ---
# Поменяйте 'flask_app' на имя вашего основного файла (без .py)
# Например, если ваш файл называется 'app.py', оставьте 'app'
APPLICATION_MODULE = 'run'
# ---------------------------------

# Добавляем текущую папку в пути Python
sys.path.append(os.getcwd())

# Импортируем объект приложения Flask
from flask import Flask
# Импортируем ваш файл как модуль
app_module = __import__(APPLICATION_MODULE)

# Passenger ожидает объект с именем 'application'
# Ваш объект Flask может называться 'app', создаем алиас
application = app_module.app

# Если ваш объект Flask называется 'application', можно проще:
# from app import application