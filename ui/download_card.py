"""
download_card.py — Виджет-карточка для отображения одной загрузки.
"""

import os
import subprocess
import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QProgressBar, QPushButton, QWidget, QSizePolicy,
)

from ui.styles import (
    SUCCESS_GREEN, ERROR_RED, WARNING_YELLOW,
    TEXT_SECONDARY, TEXT_MUTED, BG_CARD, BORDER_COLOR,
)


class DownloadCard(QFrame):
    """Карточка одной загрузки с превью, прогрессом и кнопками управления."""

    def __init__(self, title: str, thumbnail_pixmap: QPixmap = None, parent=None):
        super().__init__(parent)
        self.setObjectName("downloadCard")
        self.filepath = ""
        self._setup_ui(title, thumbnail_pixmap)

    def _setup_ui(self, title: str, thumbnail_pixmap: QPixmap):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Превью (маленькое)
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(80, 45)
        self.thumb_label.setStyleSheet(f"""
            background-color: #252525;
            border-radius: 6px;
        """)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if thumbnail_pixmap:
            scaled = thumbnail_pixmap.scaled(
                80, 45,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.thumb_label.setPixmap(scaled)
        else:
            self.thumb_label.setText("🎬")
            self.thumb_label.setStyleSheet(f"""
                background-color: #252525;
                border-radius: 6px;
                font-size: 20px;
            """)
        layout.addWidget(self.thumb_label)

        # Центральная часть: название + прогресс + статус
        center = QVBoxLayout()
        center.setSpacing(4)

        # Название
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.title_label.setMaximumWidth(400)
        self.title_label.setWordWrap(False)
        elided = self.title_label.fontMetrics().elidedText(
            title, Qt.TextElideMode.ElideRight, 400
        )
        self.title_label.setText(elided)
        center.addWidget(self.title_label)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setFixedHeight(18)
        center.addWidget(self.progress_bar)

        # Статус: скорость / ETA
        self.status_label = QLabel("Ожидание...")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY};")
        center.addWidget(self.status_label)

        layout.addLayout(center, 1)

        # Правая часть: кнопки
        buttons = QVBoxLayout()
        buttons.setSpacing(4)
        buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Кнопка отмены
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setToolTip("Отменить загрузку")
        self.cancel_btn.setFixedSize(32, 32)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                font-size: 14px;
                color: {TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background-color: {ERROR_RED};
                color: white;
                border-color: {ERROR_RED};
            }}
        """)
        buttons.addWidget(self.cancel_btn)

        # Кнопка открыть файл (скрыта до завершения)
        self.open_btn = QPushButton("📂")
        self.open_btn.setObjectName("folderBtn")
        self.open_btn.setToolTip("Открыть папку")
        self.open_btn.setFixedSize(32, 32)
        self.open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                font-size: 14px;
                color: {TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background-color: {SUCCESS_GREEN};
                color: white;
                border-color: {SUCCESS_GREEN};
            }}
        """)
        self.open_btn.setVisible(False)
        self.open_btn.clicked.connect(self._open_folder)
        buttons.addWidget(self.open_btn)

        layout.addLayout(buttons)

    def update_progress(self, data: dict):
        """Обновить прогресс загрузки."""
        percent = data.get("percent", 0)
        speed = data.get("speed", "")
        eta = data.get("eta", "")
        downloaded = data.get("downloaded", "")
        total = data.get("total", "")

        self.progress_bar.setValue(int(percent))

        parts = []
        if speed and speed != "N/A":
            parts.append(f"⚡ {speed}")
        if eta and eta != "N/A":
            parts.append(f"⏱ {eta}")
        if downloaded:
            size_str = downloaded
            if total and total != "?":
                size_str += f" / {total}"
            parts.append(size_str)

        self.status_label.setText("  •  ".join(parts) if parts else f"{percent:.0f}%")

    def set_status(self, text: str):
        """Установить текстовый статус."""
        self.status_label.setText(text)

    def set_finished(self, filepath: str):
        """Отметить загрузку как завершённую."""
        self.filepath = filepath
        self.progress_bar.setValue(100)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background: {SUCCESS_GREEN};
                border-radius: 6px;
            }}
        """)

        filename = os.path.basename(filepath)
        size_mb = ""
        try:
            size = os.path.getsize(filepath)
            size_mb = f" • {size / (1024*1024):.1f} MB"
        except OSError:
            pass

        self.status_label.setText(f"✅ Готово{size_mb}")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {SUCCESS_GREEN};")
        self.cancel_btn.setVisible(False)
        self.open_btn.setVisible(True)

    def set_error(self, message: str):
        """Отметить загрузку как ошибочную."""
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background: {ERROR_RED};
                border-radius: 6px;
            }}
        """)
        short_msg = message[:80] + "..." if len(message) > 80 else message
        self.status_label.setText(f"❌ {short_msg}")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {ERROR_RED};")
        self.cancel_btn.setVisible(False)

    def set_cancelled(self):
        """Отметить загрузку как отменённую."""
        self.status_label.setText("⏹ Отменено")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        self.cancel_btn.setVisible(False)

    def _open_folder(self):
        """Открыть папку с файлом в проводнике."""
        if not self.filepath or not os.path.exists(self.filepath):
            return

        if sys.platform == "win32":
            subprocess.Popen(f'explorer /select,"{self.filepath}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", self.filepath])
        else:
            folder = os.path.dirname(self.filepath)
            subprocess.Popen(["xdg-open", folder])
