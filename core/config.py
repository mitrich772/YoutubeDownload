"""
config.py — Центральный конфиг приложения YouTube Downloader.
Все параметры по умолчанию собраны здесь.
"""

import os

# ===== Приложение =====
APP_NAME = "YouTube Downloader"
ORG_NAME = "YTDownloader"
APP_FONT = "Segoe UI"
APP_FONT_SIZE = 10

# ===== Настройки по умолчанию =====
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
DEFAULT_FORMAT = "1080p"
DEFAULT_SMART_PASTE = False
DEFAULT_MAX_CONCURRENT = 3
DEFAULT_LOG_TO_FILE = True

# ===== Логирование =====
LOG_FILENAME = "youtube_downloader.log"
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LOGGER_NAME = "YTDownloader"

# ===== Путь к файлу настроек =====
SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"), ".youtube_downloader_settings.json"
)
