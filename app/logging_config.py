"""Настройка логирования Flask-приложения (stderr + опционально файл)."""
from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from config import _PROJECT_ROOT


def _log_level() -> int:
    name = os.environ.get('LOG_LEVEL', 'INFO').upper()
    return getattr(logging, name, logging.INFO)


def _log_file_path() -> Optional[str]:
    """
    LOG_FILE не задан — пишем в logs/app.log в корне проекта.
    LOG_FILE пустой / none / false / 0 — только stderr, без файла.
    Иначе — абсолютный или относительный путь к файлу.
    """
    raw = os.environ.get('LOG_FILE')
    if raw is None:
        return os.path.join(_PROJECT_ROOT, 'logs', 'app.log')
    s = raw.strip()
    if not s or s.lower() in ('none', 'false', '0'):
        return None
    return os.path.abspath(s)


def configure_logging(app) -> None:
    if getattr(app, '_logging_configured', False):
        return
    app._logging_configured = True

    level = _log_level()
    fmt = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    app.logger.handlers.clear()
    app.logger.setLevel(level)
    app.logger.propagate = False

    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    sh.setLevel(level)
    app.logger.addHandler(sh)

    path = _log_file_path()
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fh = RotatingFileHandler(
            path,
            maxBytes=512 * 1024,
            backupCount=5,
            encoding='utf-8',
        )
        fh.setFormatter(fmt)
        fh.setLevel(level)
        app.logger.addHandler(fh)

    # Ошибки SQL (запросы не спамим; при проблемах с БД будет видно)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
