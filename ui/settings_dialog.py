"""
settings_dialog.py — Диалог настроек приложения.
"""

import os
import re
import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox,
    QFileDialog, QGroupBox, QSpacerItem,
    QSizePolicy,
)

from core.config import (
    SETTINGS_FILE,
    DEFAULT_OUTPUT_DIR, DEFAULT_FORMAT,
    DEFAULT_SMART_PASTE, DEFAULT_MAX_CONCURRENT,
    DEFAULT_LOG_TO_FILE,
)
from core.logger import set_log_to_file

DEFAULT_SETTINGS = {
    "output_dir": DEFAULT_OUTPUT_DIR,
    "default_format": DEFAULT_FORMAT,
    "smart_paste": DEFAULT_SMART_PASTE,
    "max_concurrent": DEFAULT_MAX_CONCURRENT,
    "log_to_file": DEFAULT_LOG_TO_FILE,
}


def load_settings() -> dict:
    """Загрузить настройки из файла."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            settings = DEFAULT_SETTINGS.copy()
            settings.update(saved)
            return settings
    except Exception:
        pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """Сохранить настройки в файл."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


class SettingsDialog(QDialog):
    """Диалог настроек приложения."""

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings.copy()
        self.setWindowTitle("⚙  Настройки")
        self.setFixedSize(580, 540)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # === Заголовок ===
        header = QLabel("⚙  Настройки")
        header.setObjectName("headerLabel")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        # === Папка сохранения ===
        dir_group = QGroupBox("📁  Папка сохранения")
        dir_layout = QHBoxLayout(dir_group)
        dir_layout.setContentsMargins(12, 24, 12, 12)

        self.dir_input = QLineEdit(self.settings.get("output_dir", ""))
        self.dir_input.setPlaceholderText("Путь к папке сохранения...")
        dir_layout.addWidget(self.dir_input, 1)

        browse_btn = QPushButton("Обзор")
        browse_btn.clicked.connect(self._browse_dir)
        dir_layout.addWidget(browse_btn)

        layout.addWidget(dir_group)

        # === Параметры по умолчанию ===
        quality_group = QGroupBox("🎬  Параметры по умолчанию")
        quality_inner = QVBoxLayout(quality_group)
        quality_inner.setContentsMargins(12, 24, 12, 12)
        quality_inner.setSpacing(12)

        # Качество
        q_row = QHBoxLayout()
        q_label = QLabel("Качество:")
        q_label.setFixedWidth(120)
        q_row.addWidget(q_label)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p"])
        current_fmt = self.settings.get("default_format", DEFAULT_FORMAT)
        for i in range(self.format_combo.count()):
            if current_fmt in self.format_combo.itemText(i):
                self.format_combo.setCurrentIndex(i)
                break
        q_row.addWidget(self.format_combo, 1)
        quality_inner.addLayout(q_row)

        # Макс загрузок
        c_row = QHBoxLayout()
        c_label = QLabel("Макс. загрузок:")
        c_label.setFixedWidth(120)
        c_row.addWidget(c_label)
        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(["1", "2", "3", "4", "5"])
        current_max = str(self.settings.get("max_concurrent", DEFAULT_MAX_CONCURRENT))
        idx = self.concurrent_combo.findText(current_max)
        if idx >= 0:
            self.concurrent_combo.setCurrentIndex(idx)
        c_row.addWidget(self.concurrent_combo, 1)
        quality_inner.addLayout(c_row)

        layout.addWidget(quality_group)

        # === Функции ===
        features_group = QGroupBox("✨  Функции")
        features_layout = QVBoxLayout(features_group)
        features_layout.setContentsMargins(12, 24, 12, 12)
        features_layout.setSpacing(8)

        self.smart_paste_cb = QCheckBox("Smart Paste — автоподхват ссылки из буфера обмена")
        self.smart_paste_cb.setChecked(self.settings.get("smart_paste", DEFAULT_SMART_PASTE))
        features_layout.addWidget(self.smart_paste_cb)

        self.log_to_file_cb = QCheckBox("📝  Записывать лог в файл (youtube_downloader.log)")
        self.log_to_file_cb.setChecked(self.settings.get("log_to_file", DEFAULT_LOG_TO_FILE))
        features_layout.addWidget(self.log_to_file_cb)

        layout.addWidget(features_group)

        # === Спейсер ===
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # === Кнопки ===
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾  Сохранить")
        save_btn.setObjectName("downloadBtn")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _browse_dir(self):
        """Открыть диалог выбора папки."""
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения",
            self.dir_input.text()
        )
        if folder:
            self.dir_input.setText(folder)

    def _save(self):
        """Сохранить настройки и закрыть."""
        self.settings["output_dir"] = self.dir_input.text()

        fmt_text = self.format_combo.currentText()
        match = re.search(r'(\d+p)', fmt_text)
        self.settings["default_format"] = match.group(1) if match else DEFAULT_FORMAT

        self.settings["max_concurrent"] = int(self.concurrent_combo.currentText())
        self.settings["smart_paste"] = self.smart_paste_cb.isChecked()
        self.settings["log_to_file"] = self.log_to_file_cb.isChecked()

        # Применяем переключение лога в runtime
        set_log_to_file(self.settings["log_to_file"])

        save_settings(self.settings)
        self.accept()

    def get_settings(self) -> dict:
        """Возвращает текущие настройки."""
        return self.settings
