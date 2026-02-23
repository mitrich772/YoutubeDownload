"""
Тесты для проверки корректности конфигурации.
"""

from core.config import (
    APP_NAME,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_FORMAT,
    DEFAULT_MAX_CONCURRENT,
    DEFAULT_LOG_TO_FILE
)


def test_config_types():
    """Проверяем, что базовые константы имеют правильный тип."""
    assert isinstance(APP_NAME, str)
    assert isinstance(DEFAULT_OUTPUT_DIR, str)
    assert isinstance(DEFAULT_FORMAT, str)
    assert isinstance(DEFAULT_MAX_CONCURRENT, int)
    assert isinstance(DEFAULT_LOG_TO_FILE, bool)


def test_config_values():
    """Проверяем граничные значения ключевых констант."""
    assert DEFAULT_MAX_CONCURRENT > 0, "Количество одновременных загрузок должно быть больше 0"
    assert "p" in DEFAULT_FORMAT, "Формат по умолчанию должен содержать разрешение (например, '1080p')"
