"""
YouTube Downloader — Десктопное приложение для скачивания видео с YouTube.

Запуск: python main.py
"""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.config import APP_NAME, ORG_NAME, APP_FONT, APP_FONT_SIZE
from ui.main_window import MainWindow
from ui.styles import GLOBAL_STYLESHEET


def main():
    # Высокое DPI (для 4K мониторов)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)

    # Устанавливаем шрифт
    font = QFont(APP_FONT, APP_FONT_SIZE)
    app.setFont(font)

    # Применяем стили
    app.setStyleSheet(GLOBAL_STYLESHEET)

    # Создаём и показываем окно
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
