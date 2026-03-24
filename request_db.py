# from sqlalchemy import text
# from extensions import db
# from flask import Flask
#
# # Создаем временное приложение для работы с БД
# temp_app = Flask(__name__)
# temp_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///work_area.db'
# temp_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(temp_app)
#
# def request():
#     with temp_app.app_context():
#         # С параметрами
#         result = db.session.execute(
#             text("SELECT user_name, login FROM users;")
#     #        {"job": "developer"}
#         )
#         for row in result:
#             print(row)
#
#
# if __name__ == '__main__':
#     request()