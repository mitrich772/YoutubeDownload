"""
main_window.py — Главное окно YouTube Downloader.
"""

import os
import io
import urllib.request

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QClipboard, QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QFrame, QScrollArea,
    QApplication, QMessageBox, QSizePolicy, QSpacerItem,
)

from core.parser import parse_video, get_best_formats, is_youtube_url, VideoInfo
from core.downloader import DownloadWorker
from core.converter import check_ffmpeg
from core.logger import log
from ui.download_card import DownloadCard
from ui.settings_dialog import SettingsDialog, load_settings, save_settings
from ui.styles import (
    BG_DARK, BG_CARD, BG_INPUT, BORDER_COLOR, TEXT_SECONDARY,
    TEXT_MUTED, YOUTUBE_RED, ACCENT, ERROR_RED, SUCCESS_GREEN,
)


class FetchWorker(QThread):
    """Рабочий поток для парсинга метаданных видео."""
    finished = pyqtSignal(object)  # VideoInfo
    error = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            log.info(f"Парсинг видео: {self.url}")
            info = parse_video(self.url)
            log.info(f"Парсинг OK: {info.title} | {info.duration_str}")
            self.finished.emit(info)
        except Exception as e:
            import traceback
            log.error(f"Ошибка парсинга: {e}\n{traceback.format_exc()}")
            self.error.emit(str(e))


class ThumbnailWorker(QThread):
    """Рабочий поток для загрузки превью из сети."""
    finished = pyqtSignal(QPixmap)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            req = urllib.request.Request(self.url, headers={
                "User-Agent": "Mozilla/5.0"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.finished.emit(pixmap)
        except Exception:
            self.finished.emit(QPixmap())


class MainWindow(QMainWindow):
    """Главное окно приложения YouTube Downloader."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬  YouTube Downloader")
        self.setMinimumSize(720, 700)
        self.resize(760, 780)

        self.settings = load_settings()
        self.video_info: VideoInfo = None
        self.best_formats: list[dict] = []
        self.active_workers: list[DownloadWorker] = []
        self.thumbnail_pixmap: QPixmap = None
        self._last_clipboard = ""

        self._setup_ui()
        self._setup_smart_paste()

    def _setup_ui(self):
        """Построить интерфейс."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # ===== ЗАГОЛОВОК =====
        header_layout = QHBoxLayout()

        header_icon = QLabel("▶")
        header_icon.setStyleSheet(f"""
            font-size: 28px;
            color: {YOUTUBE_RED};
            background: transparent;
        """)
        header_layout.addWidget(header_icon)

        header_label = QLabel("YouTube Downloader")
        header_label.setObjectName("headerLabel")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Статус FFmpeg
        ffmpeg_ok = check_ffmpeg()
        ffmpeg_label = QLabel(f"{'✅' if ffmpeg_ok else '⚠️'} FFmpeg")
        ffmpeg_label.setStyleSheet(f"""
            font-size: 11px;
            color: {SUCCESS_GREEN if ffmpeg_ok else ERROR_RED};
            padding: 4px 10px;
            border: 1px solid {SUCCESS_GREEN if ffmpeg_ok else ERROR_RED};
            border-radius: 10px;
        """)
        ffmpeg_label.setToolTip(
            "FFmpeg найден" if ffmpeg_ok else
            "FFmpeg не найден! Установите FFmpeg для поддержки 1080p+ и MP3"
        )
        header_layout.addWidget(ffmpeg_label)

        # Кнопка настроек
        settings_btn = QPushButton("⚙")
        settings_btn.setToolTip("Настройки")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                font-size: 18px;
                color: {TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background-color: {BG_CARD};
                border-color: {TEXT_MUTED};
            }}
        """)
        settings_btn.clicked.connect(self._open_settings)
        header_layout.addWidget(settings_btn)

        main_layout.addLayout(header_layout)

        # ===== URL ВВОД =====
        url_layout = QHBoxLayout()
        url_layout.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("🔗  Вставьте ссылку на YouTube-видео...")
        self.url_input.returnPressed.connect(self._fetch_info)
        url_layout.addWidget(self.url_input, 1)

        self.fetch_btn = QPushButton("🔍  Найти")
        self.fetch_btn.setObjectName("fetchBtn")
        self.fetch_btn.clicked.connect(self._fetch_info)
        url_layout.addWidget(self.fetch_btn)

        main_layout.addLayout(url_layout)

        # ===== ОШИБКА =====
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        main_layout.addWidget(self.error_label)

        # ===== ИНФОРМАЦИЯ О ВИДЕО =====
        self.info_frame = QFrame()
        self.info_frame.setObjectName("infoCard")
        self.info_frame.setVisible(False)
        info_layout = QHBoxLayout(self.info_frame)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(16)

        # Превью
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(240, 135)
        self.thumbnail_label.setStyleSheet(f"""
            background-color: {BG_INPUT};
            border-radius: 10px;
        """)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setText("📷")
        self.thumbnail_label.setStyleSheet(f"""
            background-color: {BG_INPUT};
            border-radius: 10px;
            font-size: 36px;
        """)
        info_layout.addWidget(self.thumbnail_label)

        # Правая часть: мета + кнопки
        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)

        self.title_label = QLabel("Название видео")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(50)
        right_layout.addWidget(self.title_label)

        self.meta_label = QLabel("Канал • Длительность")
        self.meta_label.setObjectName("subtitleLabel")
        right_layout.addWidget(self.meta_label)

        right_layout.addSpacerItem(QSpacerItem(0, 8))

        # Выбор формата
        format_layout = QHBoxLayout()
        format_layout.setSpacing(8)

        format_label = QLabel("Формат:")
        format_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        format_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.setMinimumWidth(220)
        format_layout.addWidget(self.format_combo, 1)

        right_layout.addLayout(format_layout)

        # Кнопки скачивания
        dl_layout = QHBoxLayout()
        dl_layout.setSpacing(10)

        self.download_btn = QPushButton("📥  Скачать видео")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self._download_video)
        dl_layout.addWidget(self.download_btn)

        self.mp3_btn = QPushButton("🎵  Скачать MP3")
        self.mp3_btn.setObjectName("mp3Btn")
        self.mp3_btn.clicked.connect(self._download_mp3)
        dl_layout.addWidget(self.mp3_btn)

        right_layout.addLayout(dl_layout)

        info_layout.addLayout(right_layout, 1)
        main_layout.addWidget(self.info_frame)

        # ===== СЕКЦИЯ ЗАГРУЗОК =====
        downloads_header = QLabel("📦  Загрузки")
        downloads_header.setObjectName("sectionLabel")
        main_layout.addWidget(downloads_header)

        # Скроллируемый список загрузок
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        self.downloads_layout.setContentsMargins(0, 0, 0, 0)
        self.downloads_layout.setSpacing(8)
        self.downloads_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Плейсхолдер
        self.empty_label = QLabel("Нет активных загрузок")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 14px;
            padding: 40px;
        """)
        self.downloads_layout.addWidget(self.empty_label)

        scroll.setWidget(self.downloads_container)
        main_layout.addWidget(scroll, 1)

        # ===== СТАТУС-БАР =====
        status_layout = QHBoxLayout()

        smart_paste_status = "Вкл" if self.settings.get("smart_paste", True) else "Выкл"
        self.smart_paste_label = QLabel(f"📋 Smart Paste: {smart_paste_status}")
        self.smart_paste_label.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        status_layout.addWidget(self.smart_paste_label)

        status_layout.addStretch()

        save_dir = self.settings.get("output_dir", "")
        self.dir_label = QLabel(f"📁 {save_dir}")
        self.dir_label.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        status_layout.addWidget(self.dir_label)

        main_layout.addLayout(status_layout)

    def _setup_smart_paste(self):
        """Настроить мониторинг буфера обмена (Smart Paste)."""
        if not self.settings.get("smart_paste", True):
            return

        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.timeout.connect(self._check_clipboard)
        self.clipboard_timer.start(1000)  # Проверяем каждую секунду

    def _check_clipboard(self):
        """Проверить буфер обмена на YouTube-ссылку."""
        if not self.settings.get("smart_paste", True):
            return

        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()

        if text and text != self._last_clipboard and is_youtube_url(text):
            self._last_clipboard = text
            # Вставляем в поле только если оно пустое или содержит старую ссылку
            current = self.url_input.text().strip()
            if not current or is_youtube_url(current):
                self.url_input.setText(text)
                # Автоматически загружаем инфо
                self._fetch_info()

    def _fetch_info(self):
        """Загрузить метаданные видео по URL."""
        url = self.url_input.text().strip()
        if not url:
            self._show_error("Введите ссылку на YouTube-видео")
            return

        if not is_youtube_url(url):
            self._show_error("Некорректная ссылка. Поддерживаются: youtube.com, youtu.be")
            return

        # Блокируем UI
        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("⏳  Загрузка...")
        self.info_frame.setVisible(False)
        self._hide_error()

        # Запускаем парсинг в отдельном потоке
        self.fetch_worker = FetchWorker(url)
        self.fetch_worker.finished.connect(self._on_info_fetched)
        self.fetch_worker.error.connect(self._on_info_error)
        self.fetch_worker.start()

    def _on_info_fetched(self, info: VideoInfo):
        """Обработка успешного парсинга метаданных."""
        self.video_info = info
        self.best_formats = get_best_formats(info)

        # Обновляем UI
        self.title_label.setText(info.title)
        self.meta_label.setText(f"👤 {info.channel}  •  ⏱ {info.duration_str}")

        # Заполняем комбобокс форматов
        self.format_combo.clear()
        for fmt in self.best_formats:
            if fmt["type"] == "video":
                label = fmt["label"]
                if fmt.get("filesize_mb"):
                    label += f"  (~{fmt['filesize_mb']} MB)"
                self.format_combo.addItem(label)

        # Показываем панель
        self.info_frame.setVisible(True)
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("🔍  Найти")
        self.download_btn.setEnabled(True)
        self.mp3_btn.setEnabled(True)

        # Загружаем превью
        if info.thumbnail:
            self.thumb_worker = ThumbnailWorker(info.thumbnail)
            self.thumb_worker.finished.connect(self._on_thumbnail_loaded)
            self.thumb_worker.start()

    def _on_thumbnail_loaded(self, pixmap: QPixmap):
        """Обработка загруженного превью."""
        if pixmap.isNull():
            return
        self.thumbnail_pixmap = pixmap
        scaled = pixmap.scaled(
            240, 135,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.thumbnail_label.setPixmap(scaled)
        self.thumbnail_label.setStyleSheet(f"""
            background-color: {BG_INPUT};
            border-radius: 10px;
        """)

    def _on_info_error(self, message: str):
        """Обработка ошибки парсинга."""
        self._show_error(f"Ошибка: {message}")
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("🔍  Найти")

    def _download_video(self):
        """Начать скачивание видео в выбранном формате."""
        if not self.video_info or not self.best_formats:
            return

        # Находим выбранный формат (только видео)
        video_formats = [f for f in self.best_formats if f["type"] == "video"]
        idx = self.format_combo.currentIndex()
        if idx < 0 or idx >= len(video_formats):
            return

        chosen = video_formats[idx]
        self._start_download(chosen)

    def _download_mp3(self):
        """Начать скачивание только аудио (MP3)."""
        if not self.video_info or not self.best_formats:
            return

        # Ищем audio-формат
        audio_formats = [f for f in self.best_formats if f["type"] == "audio"]
        if not audio_formats:
            self._show_error("Аудио-формат не найден")
            return

        self._start_download(audio_formats[0])

    def _start_download(self, format_choice: dict):
        """Создать и запустить рабочий поток загрузки."""
        # Скрываем placeholder
        self.empty_label.setVisible(False)

        # Создаём карточку
        card = DownloadCard(self.video_info.title, self.thumbnail_pixmap)
        self.downloads_layout.insertWidget(0, card)  # Новые — сверху

        # Создаём worker
        output_dir = self.settings.get("output_dir", os.path.expanduser("~/Downloads"))
        os.makedirs(output_dir, exist_ok=True)

        worker = DownloadWorker(
            url=self.video_info.url,
            format_choice=format_choice,
            output_dir=output_dir,
        )

        # Подключаем сигналы
        worker.progress.connect(card.update_progress)
        worker.status_update.connect(card.set_status)
        worker.finished.connect(lambda path, c=card: c.set_finished(path))
        worker.finished.connect(lambda path, w=worker: self._on_worker_finished(w))
        worker.error.connect(lambda msg, c=card: c.set_error(msg))
        worker.error.connect(lambda msg, w=worker: self._on_worker_finished(w))

        # Кнопка отмены
        card.cancel_btn.clicked.connect(lambda _, w=worker, c=card: self._cancel_download(w, c))

        # Сохраняем и запускаем
        self.active_workers.append(worker)
        worker.start()

    def _cancel_download(self, worker: DownloadWorker, card: DownloadCard):
        """Отменить загрузку."""
        worker.cancel()
        card.set_cancelled()
        self._on_worker_finished(worker)

    def _on_worker_finished(self, worker: DownloadWorker):
        """Очистка после завершения worker'а."""
        if worker in self.active_workers:
            self.active_workers.remove(worker)

    def _open_settings(self):
        """Открыть диалог настроек."""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings = dialog.get_settings()
            save_settings(self.settings)
            # Обновляем статус-бар
            smart_paste_status = "Вкл" if self.settings.get("smart_paste", True) else "Выкл"
            self.smart_paste_label.setText(f"📋 Smart Paste: {smart_paste_status}")
            self.dir_label.setText(f"📁 {self.settings.get('output_dir', '')}")

    def _show_error(self, text: str):
        """Показать сообщение об ошибке."""
        log.error(f"UI Error: {text}")
        self.error_label.setText(f"⚠️  {text}")
        self.error_label.setVisible(True)

    def _hide_error(self):
        """Скрыть ошибку."""
        self.error_label.setVisible(False)
        self.error_label.setText("")
