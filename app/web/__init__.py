from app.web.auth import bp as auth_bp
from app.web.tasks import bp as tasks_bp
from app.web.users import bp as users_bp

__all__ = ['auth_bp', 'tasks_bp', 'users_bp']
