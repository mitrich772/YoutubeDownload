"""
parser.py — Извлечение метаданных YouTube-видео через yt-dlp.
"""

import re
from typing import Optional

import yt_dlp


# Паттерны YouTube URL
YOUTUBE_URL_PATTERNS = [
    r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
    r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
    r'(https?://)?youtu\.be/[\w-]+',
    r'(https?://)?(www\.)?youtube\.com/embed/[\w-]+',
]


def is_youtube_url(url: str) -> bool:
    """Проверяет, является ли строка валидным YouTube URL."""
    for pattern in YOUTUBE_URL_PATTERNS:
        if re.match(pattern, url.strip()):
            return True
    return False


def normalize_url(url: str) -> str:
    """Нормализует YouTube URL (shorts, youtu.be → стандартный формат)."""
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url


class VideoFormat:
    """Информация о доступном формате видео."""

    def __init__(self, format_id: str, ext: str, resolution: str,
                 filesize: Optional[int], vcodec: str, acodec: str,
                 fps: Optional[int], tbr: Optional[float], format_note: str,
                 height: Optional[int] = None, width: Optional[int] = None):
        self.format_id = format_id
        self.ext = ext
        self.resolution = resolution
        self.filesize = filesize
        self.vcodec = vcodec
        self.acodec = acodec
        self.fps = fps
        self.tbr = tbr
        self.format_note = format_note
        self.height = height or 0
        self.width = width or 0

    @property
    def has_video(self) -> bool:
        return self.vcodec != "none" and self.vcodec is not None

    @property
    def has_audio(self) -> bool:
        return self.acodec != "none" and self.acodec is not None

    @property
    def filesize_mb(self) -> Optional[float]:
        if self.filesize:
            return round(self.filesize / (1024 * 1024), 1)
        return None

    @property
    def display_name(self) -> str:
        """Человекочитаемое название формата."""
        parts = []
        if self.height > 0:
            parts.append(f"{self.height}p")
        elif self.resolution and self.resolution != "audio only":
            parts.append(self.resolution)
        if self.fps and self.fps > 30:
            parts.append(f"{self.fps}fps")
        parts.append(self.ext.upper())
        if self.filesize_mb:
            parts.append(f"~{self.filesize_mb} MB")
        elif self.tbr:
            parts.append(f"~{self.tbr:.0f}kbps")
        return " • ".join(parts)

    def __repr__(self):
        return f"<VideoFormat {self.format_id}: {self.display_name}>"


class VideoInfo:
    """Метаданные YouTube-видео."""

    def __init__(self, url: str, title: str, duration: int, channel: str,
                 thumbnail: str, video_id: str, formats: list[VideoFormat]):
        self.url = url
        self.title = title
        self.duration = duration
        self.channel = channel
        self.thumbnail = thumbnail
        self.video_id = video_id
        self.formats = formats

    @property
    def duration_str(self) -> str:
        """Длительность в формате MM:SS или HH:MM:SS."""
        h, remainder = divmod(self.duration, 3600)
        m, s = divmod(remainder, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"


def parse_video(url: str) -> VideoInfo:
    """
    Извлекает метаданные видео по URL.
    Возвращает объект VideoInfo с отфильтрованными форматами.
    """
    url = normalize_url(url)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # Собираем форматы
    raw_formats = info.get("formats", [])
    formats: list[VideoFormat] = []

    for f in raw_formats:
        vcodec = f.get("vcodec", "none") or "none"
        acodec = f.get("acodec", "none") or "none"
        resolution = f.get("resolution", "")
        ext = f.get("ext", "")
        format_note = f.get("format_note", "")

        # Пропускаем storyboard / манифесты
        if "storyboard" in format_note.lower():
            continue
        if ext in ("mhtml",):
            continue

        fmt = VideoFormat(
            format_id=f.get("format_id", ""),
            ext=ext,
            resolution=resolution,
            filesize=f.get("filesize") or f.get("filesize_approx"),
            vcodec=vcodec,
            acodec=acodec,
            fps=f.get("fps"),
            tbr=f.get("tbr"),
            format_note=format_note,
            height=f.get("height"),      # Реальная высота из yt-dlp
            width=f.get("width"),        # Реальная ширина из yt-dlp
        )
        formats.append(fmt)

    # Сортировка: по высоте по убыванию
    formats.sort(key=lambda x: -(x.height or 0))

    return VideoInfo(
        url=url,
        title=info.get("title", "Unknown"),
        duration=info.get("duration", 0) or 0,
        channel=info.get("channel", "") or info.get("uploader", "Unknown"),
        thumbnail=info.get("thumbnail", ""),
        video_id=info.get("id", ""),
        formats=formats,
    )


def get_best_formats(video_info: VideoInfo) -> list[dict]:
    """
    Возвращает список «удобных» форматов для UI:
    - bestvideo+bestaudio для каждого уникального разрешения (по высоте)
    - best audio only
    """
    seen_heights = set()
    result = []

    # Видео-форматы
    for f in video_info.formats:
        if not f.has_video:
            continue
        if f.height < 240:
            continue

        # Группируем по стандартным разрешениям
        h = f.height
        if h in seen_heights:
            continue
        seen_heights.add(h)

        result.append({
            "label": f"{h}p • MP4",
            "format_id": f.format_id,
            "resolution": f"{h}p",
            "height": h,
            "has_audio": f.has_audio,
            "filesize_mb": f.filesize_mb,
            "type": "video",
        })

    # Аудио-only (лучший)
    audio_formats = [f for f in video_info.formats if not f.has_video and f.has_audio]
    if audio_formats:
        best_audio = max(audio_formats, key=lambda x: x.tbr or 0)
        result.append({
            "label": "MP3 • Audio Only",
            "format_id": best_audio.format_id,
            "resolution": "audio",
            "height": 0,
            "has_audio": True,
            "filesize_mb": best_audio.filesize_mb,
            "type": "audio",
        })

    return result
