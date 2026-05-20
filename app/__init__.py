import os
from flask import Flask, request, session
from werkzeug.exceptions import HTTPException

from extensions import db, bcrypt
from config import Config
from .logging_config import configure_logging
from .utils.filters import b64encode_filter

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(_BASE_DIR, 'templates'),
    )
    app.config.from_object(config_object)
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

    db.init_app(app)
    bcrypt.init_app(app)

    from .api import api_v2
    from .web import auth_bp, tasks_bp, users_bp

    app.register_blueprint(api_v2)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)

    app.add_template_filter(b64encode_filter, name='b64encode')

    @app.context_processor
    def inject_api_auth():
        return {
            'api_token': session.get('access_token', ''),
            'api_base': '/v2',
        }

    configure_logging(app)

    @app.errorhandler(Exception)
    def log_unhandled_exception(exc):
        if isinstance(exc, HTTPException):
            return exc
        app.logger.exception('%s %s', request.method, request.path)
        if request.path.startswith('/v2'):
            from flask import jsonify
            return jsonify(code=500, message='Внутренняя ошибка сервера'), 500
        return 'Internal Server Error', 500

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    return app
