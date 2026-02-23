"""
styles.py — Dark Mode QSS стили для YouTube Downloader.
"""

# Акцентные цвета
YOUTUBE_RED = "#FF0000"
ACCENT = "#FF4444"
ACCENT_HOVER = "#FF6666"
ACCENT_DARK = "#CC0000"

BG_DARK = "#0F0F0F"
BG_CARD = "#1A1A1A"
BG_INPUT = "#252525"
BG_HOVER = "#2A2A2A"
BG_BUTTON = "#303030"

TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#AAAAAA"
TEXT_MUTED = "#666666"

BORDER_COLOR = "#333333"
BORDER_FOCUS = "#FF4444"

SUCCESS_GREEN = "#4CAF50"
WARNING_YELLOW = "#FFC107"
ERROR_RED = "#F44336"


GLOBAL_STYLESHEET = f"""
/* ===== ГЛОБАЛЬНЫЕ СТИЛИ ===== */

QMainWindow, QDialog {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
}}

QWidget {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}

/* ===== КНОПКИ ===== */

QPushButton {{
    background-color: {BG_BUTTON};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 13px;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: {TEXT_MUTED};
}}

QPushButton:pressed {{
    background-color: {BG_INPUT};
}}

QPushButton:disabled {{
    background-color: {BG_INPUT};
    color: {TEXT_MUTED};
    border-color: {BG_INPUT};
}}

/* Акцентная кнопка (скачать) */
QPushButton#downloadBtn, QPushButton#mp3Btn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {YOUTUBE_RED}, stop:1 {ACCENT});
    border: none;
    color: white;
    font-size: 14px;
    padding: 12px 28px;
    border-radius: 10px;
}}

QPushButton#downloadBtn:hover, QPushButton#mp3Btn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT}, stop:1 {ACCENT_HOVER});
}}

QPushButton#downloadBtn:pressed, QPushButton#mp3Btn:pressed {{
    background: {ACCENT_DARK};
}}

QPushButton#downloadBtn:disabled, QPushButton#mp3Btn:disabled {{
    background: {BG_BUTTON};
    color: {TEXT_MUTED};
}}

/* Кнопка поиска */
QPushButton#fetchBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {YOUTUBE_RED}, stop:1 {ACCENT});
    border: none;
    color: white;
    font-size: 14px;
    padding: 12px 24px;
    border-radius: 10px;
    min-width: 100px;
}}

QPushButton#fetchBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT}, stop:1 {ACCENT_HOVER});
}}

QPushButton#fetchBtn:disabled {{
    background: {BG_BUTTON};
    color: {TEXT_MUTED};
}}

/* Маленькие кнопки управления */
QPushButton#cancelBtn, QPushButton#openBtn, QPushButton#folderBtn {{
    padding: 6px 12px;
    font-size: 12px;
    min-height: 16px;
    border-radius: 6px;
}}

/* ===== ПОЛЯ ВВОДА ===== */

QLineEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 2px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: {ACCENT};
}}

QLineEdit:focus {{
    border-color: {BORDER_FOCUS};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

/* ===== КОМБОБОКС ===== */

QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 2px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 20px;
}}

QComboBox:hover {{
    border-color: {TEXT_MUTED};
}}

QComboBox:focus {{
    border-color: {BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT_SECONDARY};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    selection-background-color: {ACCENT};
    outline: none;
    padding: 4px;
}}

/* ===== ПРОГРЕСС-БАР ===== */

QProgressBar {{
    background-color: {BG_INPUT};
    border: none;
    border-radius: 9px;
    text-align: center;
    color: {TEXT_PRIMARY};
    font-size: 11px;
    font-weight: bold;
    min-height: 18px;
    max-height: 18px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {YOUTUBE_RED}, stop:1 {ACCENT_HOVER});
    border-radius: 9px;
}}

/* ===== СКРОЛЛБАР ===== */

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background-color: {BG_DARK};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {TEXT_MUTED};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {TEXT_SECONDARY};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ===== ЛЕЙБЛЫ ===== */

QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#titleLabel {{
    font-size: 16px;
    font-weight: bold;
}}

QLabel#subtitleLabel {{
    font-size: 13px;
    color: {TEXT_SECONDARY};
}}

QLabel#headerLabel {{
    font-size: 22px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QLabel#sectionLabel {{
    font-size: 14px;
    font-weight: bold;
    color: {TEXT_SECONDARY};
    padding: 8px 0 4px 0;
}}

QLabel#errorLabel {{
    color: {ERROR_RED};
    font-size: 12px;
}}

QLabel#successLabel {{
    color: {SUCCESS_GREEN};
    font-size: 12px;
}}

/* ===== ФРЕЙМЫ / КАРТОЧКИ ===== */

QFrame#infoCard, QFrame#downloadCard {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_COLOR};
    border-radius: 12px;
    padding: 16px;
}}

QFrame#infoCard:hover {{
    border-color: {TEXT_MUTED};
}}

/* ===== ЧЕКБОКСЫ ===== */

QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {BORDER_COLOR};
    border-radius: 4px;
    background-color: {BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}

QCheckBox::indicator:hover {{
    border-color: {TEXT_MUTED};
}}

/* ===== TOOLTIP ===== */

QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ===== GROUP BOX ===== */

QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 20px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: {TEXT_SECONDARY};
}}
"""
