import telebot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from PIL import Image, ImageDraw, ImageFont
import io
import os
import logging
import threading
from PIL import Image, ImageDraw, ImageFont
import textwrap


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7997248089:AAFPNCq42ZsC7yGLydXG5KS5CBPbjIzZL5Q"

bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения выбранного шаблона
user_templates = {}
template_cache = {}
font_cache = {}
font_path = os.path.join(BASE_DIR, "fonts", "festive.ttf")

# КОНФИГУРАЦИЯ ШАБЛОНОВ
TEMPLATE_CONFIGS = {
    "template_1": {
        "name": "🍊 Мандаринка",
        "description": "Классическая новогодняя открытка с мандаринкой",
        "image_path": os.path.join(BASE_DIR, "templates", "card1.png"),
        "image_path": os.path.join(BASE_DIR, "templates", "card1.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 100,
            "color": "white"
        },
        "text_position": {
            "x": "center",
            "y": 1000,
            "max_width": 800,
            "line_height": 70
        }
    },
    "template_2": {
        "name": "❄️ Снежок",
        "description": "Зимний пейзаж с снежинками и праздничной атмосферой",
        "image_path": os.path.join(BASE_DIR, "templates", "card2.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 28,
            "color": "#07381F"
        },
        "text_position": {
            "x": 150,
            "y": 150,
            "max_width": 300,
            "line_height": 50
        }
    },
    "template_3": {
        "name": "⭐️ Зимнее утро",
        "description": "Зимнее утро с ярким солнцем и снегом",
        "image_path": os.path.join(BASE_DIR, "templates", "card3.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 200,
            "color": "white"
        },
        "text_position": {
            "x": "center",
            "y": 150,
            "max_width": 2000,
            "line_height": 200
        }
    }
}


# Функция для предзагрузки ресурсов
def load_resources():
    logger.info("Preloading resources...")

    for template_id, config in TEMPLATE_CONFIGS.items():
        try:
            # Загружаем шаблоны
            image_path = config["image_path"]
            if os.path.exists(image_path):
                img = Image.open(image_path)
                template_cache[template_id] = img
                logger.info(f"✓ Loaded template: {template_id}")
            else:
                logger.error(f"✗ Missing template: {image_path}")

            # Шрифты теперь загружаются динамически, так что просто проверяем доступность
            if os.path.exists(font_path):
                logger.info(f"✓ Font available for: {template_id}")
            else:
                logger.warning(f"⚠ Font not found: {font_path}")

        except Exception as e:
            logger.error(f"Error loading {template_id}: {e}")

    logger.info("Resources loaded!")


# Создаем Reply-клавиатуру
main_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
)
main_keyboard.add(KeyboardButton("🎨 Создать открытку"))
main_keyboard.add(KeyboardButton("👀 Посмотреть шаблоны"), KeyboardButton("ℹ️ Помощь"))


# /start — приветствие
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🎄 *Привет! Я бот для создания новогодних открыток!* 

Я помогу тебе создать красивую поздравительную открытку с твоим текстом. 

Выбери в меню ниже, что ты хочешь сделать:
    """
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )


# Обработка кнопки "Создать открытку"
@bot.message_handler(func=lambda message: message.text == "🎨 Создать открытку")
def create_new_card(message):
    # ДИНАМИЧЕСКИ создаем кнопки из конфига шаблонов
    keyboard = InlineKeyboardMarkup(row_width=1)
    for template_id, config in TEMPLATE_CONFIGS.items():
        keyboard.add(InlineKeyboardButton(
            text=config["name"],
            callback_data=template_id
        ))

    bot.send_message(
        message.chat.id,
        "Отлично! Выбери шаблон для своей открытки:",
        reply_markup=keyboard
    )


# Обработка выбора шаблона
@bot.callback_query_handler(func=lambda call: call.data in TEMPLATE_CONFIGS.keys())
def process_template(call):
    user_id = call.from_user.id
    template_id = call.data
    user_templates[user_id] = template_id

    config = TEMPLATE_CONFIGS[template_id]

    bot.send_message(
        call.message.chat.id,
        f"✨ Отлично! Выбран шаблон: *{config['name']}*\n\n"
        f"Теперь напиши текст, который хочешь разместить на открытке.\n"
        f"Например: *«С Новым Годом! Желаю счастья!»* 🌟",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )
    bot.answer_callback_query(call.id)


# Функция создания карточки
def calculate_font_size(text, template_id):
    """Рассчитывает оптимальный размер шрифта на основе длины текста и шаблона"""
    config = TEMPLATE_CONFIGS[template_id]
    base_font_size = config["font"]["size"]

    # Базовый расчет на основе длины текста
    text_length = len(text)

    if text_length <= 15:
        font_size = base_font_size
    elif text_length <= 25:
        font_size = base_font_size * 0.75
    elif text_length <= 35:
        font_size = base_font_size * 0.65
    elif text_length <= 45:
        font_size = base_font_size * 0.55
    else:
        font_size = base_font_size * 0.45

    return max(10, int(font_size))  # Минимальный размер 10


def get_dynamic_font(template_id, text):
    font_size = calculate_font_size(text, template_id)
    try:
        font = ImageFont.truetype(font_path, font_size)
        logger.info(f"✓ Loaded dynamic font for template {template_id}: size={font_size}, text='{text}'")
        return font
    except Exception as e:
        logger.error(f"✗ Failed to load font {font_path} with size {font_size}: {e}")
        logger.info("⚠ Using fallback font")
        return ImageFont.load_default()


def create_card_sync(template_id, text):
    try:
        config = TEMPLATE_CONFIGS[template_id]

        # Используем кэшированные ресурсы
        if template_id not in template_cache:
            if not os.path.exists(config["image_path"]):
                raise FileNotFoundError(f"Template image not found: {config['image_path']}")
            template_cache[template_id] = Image.open(config["image_path"])

        img = template_cache[template_id].copy()
        draw = ImageDraw.Draw(img)

        # Получаем шрифт с динамическим размером (без учета ширины)
        font = get_dynamic_font(template_id, text)

        # Обработка переноса текста
        position_config = config["text_position"]
        max_width = position_config["max_width"]
        lines = []
        words = text.split()
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Рассчитываем общую высоту текстового блока
        line_height = position_config["line_height"]
        total_text_height = len(lines) * line_height

        # Получаем область для текста из конфигурации
        text_area_y_start = position_config["y"]
        # Если в конфиге есть высота области, используем ее, иначе рассчитываем
        if "height" in position_config:
            text_area_height = position_config["height"]
        else:
            # По умолчанию используем высоту от начальной позиции до низа изображения
            text_area_height = img.height - text_area_y_start

        # Рассчитываем вертикальное центрирование
        y_start_position = text_area_y_start + (text_area_height - total_text_height) // 2

        # Рисуем текст с выравниванием по центру
        y_position = y_start_position

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]

            # Горизонтальное центрирование
            x_position = (img.width - text_width) // 2

            draw.text((x_position, y_position), line, font=font, fill=config["font"]["color"])
            y_position += line_height

        # Сохраняем в память
        output = io.BytesIO()
        img.save(output, format="PNG", optimize=True)
        output.seek(0)

        return output

    except Exception as e:
        logger.error(f"Error in create_card_sync: {e}")
        raise



# Просмотр шаблонов
@bot.message_handler(func=lambda message: message.text == "👀 Посмотреть шаблоны")
def show_templates(message):
    try:
        templates_info = "📋 *Доступные шаблоны:*\n\n"

        for template_id, config in TEMPLATE_CONFIGS.items():
            templates_info += f"*{config['name']}*\n"
            templates_info += f"{config['description']}\n\n"

        templates_info += "Хочешь создать открытку? Нажми «🎨 Создать открытку»!"

        bot.send_message(message.chat.id, templates_info, parse_mode="Markdown")

        # Показываем превью шаблонов
        for template_id, config in TEMPLATE_CONFIGS.items():
            if os.path.exists(config["image_path"]):
                with open(config["image_path"], "rb") as f:
                    bot.send_photo(
                        message.chat.id,
                        f,
                        caption=f"{config['name']}\n{config['description']}"
                    )

    except Exception as e:
        logger.error(f"Error showing templates: {e}")
        bot.send_message(message.chat.id, "❌ Не удалось загрузить шаблоны")


# Помощь
@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def show_help(message):
    help_text = """
🤖 *Как пользоваться ботом:*

*🎨 Создать открытку:*
1. Нажми «Создать открытку»
2. Выбери понравившийся шаблон
3. Напиши текст поздравления  
4. Получи готовую открытку!

Каждый шаблон имеет свой уникальный стиль, шрифт и цвет текста! 🎨

*Приятного творчества!* ✨
    """
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")


# Обработка текста и создание открытки
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id

    # Пропускаем команды меню
    if message.text in ["🎨 Создать открытку", "👀 Посмотреть шаблоны", "ℹ️ Помощь"]:
        return

    # Проверяем, что пользователь выбрал шаблон
    if user_id not in user_templates:
        bot.send_message(
            message.chat.id,
            "Чтобы создать открытку, сначала выбери шаблон — нажми «🎨 Создать открытку» 🎅",
            reply_markup=main_keyboard
        )
        return

    # Проверяем, что сообщение не команда
    if message.text.startswith('/'):
        return

    try:
        template_id = user_templates[user_id]

        # Показываем что начали создание
        processing_msg = bot.send_message(message.chat.id, "🔄 Создаю открытку...")

        # Создаем карточку
        output = create_card_sync(template_id, message.text)

        # Удаляем сообщение "Создаю..."
        bot.delete_message(message.chat.id, processing_msg.message_id)

        # Отправляем готовую открытку
        bot.send_photo(
            message.chat.id,
            output,
            caption="🎉 *Готово! Твоя открытка создана!*\n\n"
                    "Можешь отправить её друзьям или создать ещё одну через меню ниже!",
            parse_mode="Markdown",
            reply_markup=main_keyboard
        )

    except Exception as e:
        logger.error(f"Error creating card: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при создании открытки. Попробуй еще раз.",
            reply_markup=main_keyboard
        )

    finally:
        # Удаляем выбор шаблона после отправки
        if user_id in user_templates:
            del user_templates[user_id]


# Запуск бота
if __name__ == "__main__":
    # Предзагружаем ресурсы
    load_resources()

    logger.info("🤖 Bot started!")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)