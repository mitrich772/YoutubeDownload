"""
Тесты для модуля парсинга ссылок YouTube.
"""

from core.parser import is_youtube_url, normalize_url


def test_is_youtube_url_valid():
    """Проверка валидных ссылок на YouTube."""
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/ABCDEFG123",
        "https://youtube.com/embed/dQw4w9WgXcQ",
    ]
    for url in valid_urls:
        assert is_youtube_url(url) is True, f"Не распознал валидный URL: {url}"


def test_is_youtube_url_invalid():
    """Проверка невалидных ссылок."""
    invalid_urls = [
        "https://google.com",
        "https://vk.com/video12345",
        "youtube.com",  # без протокола (мы ожидаем хотя бы youtu.be или youtube.com/watch)
        "just a random string",
        "",
    ]
    for url in invalid_urls:
        assert is_youtube_url(url) is False, f"Распознал невалидный URL: {url}"


def test_normalize_url():
    """Проверка нормализации ссылок (добавление протокола)."""
    # Без протокола -> добавляется https://
    assert normalize_url("www.youtube.com/watch?v=dQw4w9WgXcQ") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # С протоколом -> не меняется
    assert normalize_url("http://youtu.be/123") == "http://youtu.be/123"
    
    # Лишние пробелы -> убираются
    assert normalize_url("   https://youtu.be/123   ") == "https://youtu.be/123"
