"""
logger.py — Логирование приложения.
Поддерживает переключение записи в файл через настройки.
"""

import os
import logging

from core.config import (
    LOG_FILENAME, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT,
    LOG_LOGGER_NAME, DEFAULT_LOG_TO_FILE,
)

LOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(LOG_DIR, LOG_FILENAME)

# Ссылка на файловый хэндлер (нужна для переключения)
_file_handler: logging.FileHandler | None = None


def setup_logger(log_to_file: bool = DEFAULT_LOG_TO_FILE) -> logging.Logger:
    """Настраивает и возвращает логгер приложения."""
    global _file_handler

    logger = logging.getLogger(LOG_LOGGER_NAME)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Файловый хэндлер (если включён)
    if log_to_file:
        _file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        _file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
        _file_handler.setFormatter(formatter)
        logger.addHandler(_file_handler)

    # Стартовая запись
    logger.info("=" * 60)
    logger.info("YouTube Downloader запущен")
    logger.info("=" * 60)

    return logger


def set_log_to_file(enabled: bool):
    """
    Включить/выключить запись лога в файл в runtime.
    Вызывается из настроек при переключении чекбокса.
    """
    global _file_handler
    logger = logging.getLogger(LOG_LOGGER_NAME)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    if enabled and _file_handler is None:
        # Включаем файловый лог
        _file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        _file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
        _file_handler.setFormatter(formatter)
        logger.addHandler(_file_handler)
        logger.info("Логирование в файл включено")
    elif not enabled and _file_handler is not None:
        # Выключаем файловый лог
        logger.info("Логирование в файл выключено")
        logger.removeHandler(_file_handler)
        _file_handler.close()
        _file_handler = None


def _read_log_to_file_setting() -> bool:
    """Читает настройку log_to_file из JSON-файла (без импорта settings_dialog)."""
    import json
    from core.config import SETTINGS_FILE
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("log_to_file", DEFAULT_LOG_TO_FILE)
    except Exception:
        pass
    return DEFAULT_LOG_TO_FILE


# Глобальный логгер
log = setup_logger(log_to_file=_read_log_to_file_setting())
