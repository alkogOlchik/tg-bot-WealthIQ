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
        "description": "Классическая новогодняя открытка с мандаринкой",
        "image_path": os.path.join(BASE_DIR, "templates", "card1.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 100,
            "color": "white"
        },
        "text_position": {
            "x": 100,
            "y": 1150,
            "max_width": 800,
            "max_height": 300,  # ← Добавьте
            "line_height": 70,
            "min_font_size": 20,  # ← Добавьте
            "max_font_size": 150  # ← Добавьте
        }
    },
    "template_2": {
        "name": "С красной икрой",
        "description": "Зимний пейзаж с снежинками и праздничной атмосферой",
        "image_path": os.path.join(BASE_DIR, "templates", "card2.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 100,
            "color": "white"
        },
        "text_position": {
            "x": 100,
            "y": 1150,
            "max_width": 800,
            "max_height": 300,  # ← Добавьте
            "line_height": 70,
            "min_font_size": 20,  # ← Добавьте
            "max_font_size": 150  # ← Добавьте
        }
    },
    "template_3": {
        "name": "С леденцом",
        "description": "Зимнее утро с ярким солнцем и снегом",
        "image_path": os.path.join(BASE_DIR, "templates", "card3.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 100,
            "color": "white"
        },
        "text_position": {
            "x": 100,
            "y": 1150,
            "max_width": 800,
            "max_height": 300,  # ← Добавьте
            "line_height": 70,
            "min_font_size": 20,  # ← Добавьте
            "max_font_size": 150  # ← Добавьте
        }
    }
}

# Глобальные переменные
user_templates = {}
template_cache = {}
font_path = os.path.join(BASE_DIR, "fonts", "festive.ttf")

# Клавиатуры
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton("Создать открытку"))
    keyboard.add(KeyboardButton("Посмотреть шаблоны"), KeyboardButton("Помощь"))
    return keyboard