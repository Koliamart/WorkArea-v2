from flask import Blueprint

from app.api.auth_routes import bp as auth_bp
from app.api.tasks_routes import bp as tasks_bp
from app.api.users_routes import bp as users_bp

api_v2 = Blueprint('api_v2', __name__, url_prefix='/v2')
api_v2.register_blueprint(auth_bp)
api_v2.register_blueprint(users_bp)
api_v2.register_blueprint(tasks_bp)
