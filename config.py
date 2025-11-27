import os
import logging, telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7997248089:AAFPNCq42ZsC7yGLydXG5KS5CBPbjIzZL5Q"

bot = telebot.TeleBot(BOT_TOKEN)

# КОНФИГУРАЦИЯ ШАБЛОНОВ
TEMPLATE_CONFIGS = {
    "template_1": {
        "name": "С мандаринами",
        "language": "ru",
        "image_path": os.path.join(BASE_DIR, "templates", "С мандарином.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 20,
            "color": "white"
        },
        "text_position": {
            "x": "left",
            "x_offset": 100,
            "y": 750,
            "max_width": 250,
            "max_height": 150,
            "line_height": 30,
            "min_font_size": 8,
            "max_font_size": 20,
            "align": "left"
        }
    },
    "template_2": {
        "name": "С красной икрой",
        "language": "ru",
        "image_path": os.path.join(BASE_DIR, "templates", "С красной икрой.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 20,
            "color": "white"
        },
        "text_position": {
            "x": "left",
            "x_offset": 35,
            "y": 520,
            "max_width": 250,
            "max_height": 150,
            "line_height": 30,
            "min_font_size": 8,
            "max_font_size": 20,
            "align": "left"
        }
    },
    "template_3": {
        "name": "С леденцом",
        "language": "ru",
        "image_path": os.path.join(BASE_DIR, "templates", "С леденцом.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 20,
            "color": "white"
        },
        "text_position": {
            "x": "left",
            "x_offset": 35,
            "y": 520,
            "max_width": 250,
            "max_height": 150,
            "line_height": 30,
            "min_font_size": 8,
            "max_font_size": 20,
            "align": "left"
        }
    },
    "template_4": {
        "name": "Для Clussters",
        "language": "ru",
        "image_path": os.path.join(BASE_DIR, "templates", "С леденцом.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 20,
            "color": "white"
        },
        "text_position": {
            "x": "left",
            "x_offset": 35,
            "y": 520,
            "max_width": 250,
            "max_height": 150,
            "line_height": 30,
            "min_font_size": 8,
            "max_font_size": 20,
            "align": "left"
        }
    },
    "template_5": {
        "name": "Для TTA",
        "language": "ru",
        "image_path": os.path.join(BASE_DIR, "templates", "С леденцом.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 20,
            "color": "white"
        },
        "text_position": {
            "x": "left",
            "x_offset": 35,
            "y": 520,
            "max_width": 250,
            "max_height": 150,
            "line_height": 30,
            "min_font_size": 8,
            "max_font_size": 20,
            "align": "left"
        }
    },
    "template_6": {
        "name": "Для ET",
        "language": "ru",
        "image_path": os.path.join(BASE_DIR, "templates", "С леденцом.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 20,
            "color": "white"
        },
        "text_position": {
            "x": "left",
            "x_offset": 35,
            "y": 520,
            "max_width": 250,
            "max_height": 150,
            "line_height": 30,
            "min_font_size": 8,
            "max_font_size": 20,
            "align": "left"
        }
    },
    "template_7": {
        "name": "In English, please!",
        "language": "en",
        "image_path": os.path.join(BASE_DIR, "templates", "End_card.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 20,
            "color": "white"
        },
        "text_position": {
            "x": "left",
            "x_offset": 35,
            "y": 520,
            "max_width": 250,
            "max_height": 150,
            "line_height": 30,
            "min_font_size": 8,
            "max_font_size": 20,
            "align": "left"
        }
    }
    }

TEXT_TEMPLATES = {
    "ru_1": {
        "title": "Текст 1",
        "button_label": "Текст 1",
        "text": "{name}, пусть 2026 год будет таким же свежим и солнечным, как первые новогодние мандарины. С праздником вас!",
        "requires_name": True
    },
    "ru_2": {
        "title": "Текст 2",
        "button_label": "Текст 2",
        "text": "{name}, пусть 2026 принесет вам радость, вдохновение и только приятные сюрпризы! С наступающим!",
        "requires_name": True
    },
    "ru_3": {
        "title": "Текст 3",
        "button_label": "Текст 3",
        "text": "{name}, желаю, чтобы 2026 стал для вас годом больших идей, удачных решений и красивых моментов!",
        "requires_name": True
    }
}

ENG_TEXT_TEMPLATES = {
    "en_1": {
        "title": "Text",
        "button_label": "Text 1",
        "text": "May the coming year carry a sense of taste in everything you do. Wishing you joyful holidays!",
        "requires_name": False
    }
}

# Глобальные переменные
user_templates = {}
pending_text_templates = {}
template_cache = {}
font_path = os.path.join(BASE_DIR, "fonts", "festive.ttf")

# Клавиатуры
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(KeyboardButton("Создать открытку"))
    keyboard.add(KeyboardButton("Выбрать текстовку"))
    keyboard.add(KeyboardButton("Посмотреть открытки"))
    keyboard.add(KeyboardButton("Помощь"))
    return keyboard