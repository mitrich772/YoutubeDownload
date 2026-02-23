"""
downloader.py — Менеджер загрузок YouTube-видео через yt-dlp.
Работает в отдельных QThread, чтобы не блокировать UI.
"""

import os
import re
import traceback

from PyQt6.QtCore import QThread, pyqtSignal

import yt_dlp

from core.converter import check_ffmpeg, get_ffmpeg_path
from core.logger import log


class DownloadWorker(QThread):
    """
    Рабочий поток для скачивания одного видео.
    Сигналы для обновления UI.
    """

    # Сигналы
    progress = pyqtSignal(dict)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)
    merging = pyqtSignal()

    def __init__(self, url: str, format_choice: dict, output_dir: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.format_choice = format_choice
        self.output_dir = output_dir
        self._cancelled = False

    def cancel(self):
        """Отменить загрузку."""
        self._cancelled = True
        log.info(f"Загрузка отменена: {self.url}")

    def run(self):
        """Основной метод потока."""
        log.info(f"Начало загрузки: {self.url} | формат: {self.format_choice}")
        try:
            if self.format_choice["type"] == "audio":
                self._download_audio()
            else:
                self._download_video()
        except Exception as e:
            log.error(f"Ошибка загрузки: {e}\n{traceback.format_exc()}")
            if not self._cancelled:
                self.error.emit(str(e))

    @staticmethod
    def _format_bytes(b: float) -> str:
        if b < 1024:
            return f"{b:.0f} B"
        elif b < 1024 ** 2:
            return f"{b / 1024:.1f} KB"
        elif b < 1024 ** 3:
            return f"{b / (1024 ** 2):.1f} MB"
        else:
            return f"{b / (1024 ** 3):.2f} GB"

    @staticmethod
    def _format_speed(s: float) -> str:
        if s < 1024:
            return f"{s:.0f} B/s"
        elif s < 1024 ** 2:
            return f"{s / 1024:.1f} KB/s"
        else:
            return f"{s / (1024 ** 2):.1f} MB/s"

    @staticmethod
    def _format_eta(seconds: int) -> str:
        if seconds < 0:
            return "N/A"
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def _progress_hook(self, d: dict):
        """Callback от yt-dlp для отслеживания прогресса."""
        if self._cancelled:
            raise Exception("Загрузка отменена")

        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0) or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            speed = d.get("speed") or 0
            eta = d.get("eta")

            if total > 0:
                percent = min((downloaded / total) * 100, 100.0)
            else:
                percent = 0.0

            speed_str = self._format_speed(speed) if speed else "..."
            eta_str = self._format_eta(eta) if eta is not None else "..."
            downloaded_str = self._format_bytes(downloaded)
            total_str = self._format_bytes(total) if total > 0 else "?"

            self.progress.emit({
                "percent": percent,
                "speed": speed_str,
                "eta": eta_str,
                "downloaded": downloaded_str,
                "total": total_str,
            })

        elif d["status"] == "finished":
            self.progress.emit({"percent": 100.0, "speed": "", "eta": "", "downloaded": "", "total": ""})
            self.status_update.emit("Обработка...")

    def _download_video(self):
        """Скачивание видео. Автоопределение: с FFmpeg (DASH) или без (комбинированный)."""
        self.status_update.emit("Подготовка загрузки...")

        height = self.format_choice.get("height", 1080)
        has_ffmpeg = check_ffmpeg()

        log.info(f"FFmpeg доступен: {has_ffmpeg} | Запрошенное качество: {height}p")

        if has_ffmpeg:
            # С FFmpeg: скачиваем лучшее видео + лучшее аудио отдельно, затем склеиваем
            format_str = (
                f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={height}]+bestaudio/"
                f"best[height<={height}]/"
                f"best"
            )
        else:
            # Без FFmpeg: берём только комбинированные форматы (видео+аудио в одном файле)
            format_str = (
                f"best[height<={height}][ext=mp4]/"
                f"best[height<={height}]/"
                f"best[ext=mp4]/"
                f"best"
            )
            log.warning("FFmpeg не найден — используется комбинированный формат (макс ~720p)")

        ydl_opts = {
            "format": format_str,
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
        }

        # Указываем путь к FFmpeg
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_path)

        # Добавляем merge и postprocessor только если есть FFmpeg
        if has_ffmpeg:
            ydl_opts["merge_output_format"] = "mp4"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }]

        log.info(f"yt-dlp format string: {format_str}")
        self.status_update.emit("Скачивание видео...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            filepath = ydl.prepare_filename(info)

            # Логируем фактическое качество
            actual_w = info.get("width", "?")
            actual_h = info.get("height", "?")
            actual_format = info.get("format", "?")
            actual_vcodec = info.get("vcodec", "?")
            actual_acodec = info.get("acodec", "?")
            req_formats = info.get("requested_formats", [])
            if req_formats:
                parts = []
                for rf in req_formats:
                    rw = rf.get("width", "?")
                    rh = rf.get("height", "?")
                    rc = rf.get("vcodec", rf.get("acodec", "?"))
                    parts.append(f"{rw}x{rh} ({rc})")
                log.info(f"DASH потоки: {' + '.join(parts)}")
            log.info(f"Итоговое качество: {actual_w}x{actual_h} | format={actual_format} | vcodec={actual_vcodec} | acodec={actual_acodec}")

            # yt-dlp может поменять расширение после мержа
            if not os.path.exists(filepath):
                base = os.path.splitext(filepath)[0]
                for ext in (".mp4", ".mkv", ".webm"):
                    candidate = base + ext
                    if os.path.exists(candidate):
                        filepath = candidate
                        break

        if not self._cancelled:
            # Логируем размер файла
            try:
                fsize = os.path.getsize(filepath)
                log.info(f"Загрузка завершена: {filepath} | размер: {fsize / (1024*1024):.1f} MB")
            except OSError:
                log.info(f"Загрузка завершена: {filepath}")
            self.status_update.emit("Готово!")
            self.finished.emit(filepath)

    def _download_audio(self):
        """Скачивание аудио. С FFmpeg — конвертация в MP3, без — скачивание как есть."""
        self.status_update.emit("Подготовка загрузки аудио...")

        has_ffmpeg = check_ffmpeg()
        log.info(f"Загрузка аудио | FFmpeg доступен: {has_ffmpeg}")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
        }

        # Указываем путь к FFmpeg
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_path)

        if has_ffmpeg:
            # С FFmpeg — конвертируем в MP3
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            # Без FFmpeg — скачиваем аудио как есть (webm/m4a)
            log.warning("FFmpeg не найден — аудио будет скачано без конвертации в MP3")

        self.status_update.emit("Скачивание аудио...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=True)
            filepath = ydl.prepare_filename(info)

            if has_ffmpeg:
                # После конвертации расширение будет .mp3
                base = os.path.splitext(filepath)[0]
                mp3_path = base + ".mp3"
                if os.path.exists(mp3_path):
                    filepath = mp3_path

        if not self._cancelled:
            log.info(f"Загрузка аудио завершена: {filepath}")
            self.status_update.emit("Готово!")
            self.finished.emit(filepath)
