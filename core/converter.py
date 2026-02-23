"""
converter.py — Проверка FFmpeg и конвертация медиа.
"""

import shutil
import subprocess
import os
import sys


def _get_app_dir() -> str:
    """Возвращает директорию приложения."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_ffmpeg_path() -> str:
    """
    Ищет ffmpeg: сначала рядом с приложением, потом в PATH.
    Возвращает путь или пустую строку.
    """
    # 1. Рядом с приложением
    local = os.path.join(_get_app_dir(), "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if os.path.isfile(local):
        return local

    # 2. В PATH
    path = shutil.which("ffmpeg")
    return path if path else ""


def check_ffmpeg() -> bool:
    """Проверяет, доступен ли FFmpeg."""
    return bool(get_ffmpeg_path())


def get_ffprobe_path() -> str:
    """Ищет ffprobe рядом с приложением или в PATH."""
    local = os.path.join(_get_app_dir(), "ffprobe.exe" if os.name == "nt" else "ffprobe")
    if os.path.isfile(local):
        return local
    path = shutil.which("ffprobe")
    return path if path else ""
