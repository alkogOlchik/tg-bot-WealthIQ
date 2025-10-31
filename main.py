import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from PIL import Image, ImageDraw, ImageFont
import io
import os
import logging
import concurrent.futures

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7997248089:AAFPNCq42ZsC7yGLydXG5KS5CBPbjIzZL5Q"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для хранения выбранного шаблона каждым пользователем
user_templates = {}

# КЭШИ для оптимизации
template_cache = {}
font_cache = {}

# Пул потоков для тяжелых операций
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)

# КОНФИГУРАЦИЯ ШАБЛОНОВ
TEMPLATE_CONFIGS = {
    "template_1": {
        "name": "🎄 Елочка",
        "description": "Классическая новогодняя открытка с елкой и украшениями",
        "image_path": os.path.join(BASE_DIR, "templates", "card1.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 40,
            "color": "white"
        },
        "text_position": {
            "x": "center",
            "y": 150,
            "max_width": 400,
            "line_height": 50
        }
    },
    "template_2": {
        "name": "❄️ Снежок",
        "description": "Зимний пейзаж с снежинками и праздничной атмосферой",
        "image_path": os.path.join(BASE_DIR, "templates", "card2.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 36,
            "color": "#1AA87D"
        },
        "text_position": {
            "x": 200,
            "y": 150,
            "max_width": 450,
            "line_height": 45
        }
    },
    "template_3": {
        "name": "⭐️ Звездная ночь",
        "description": "Ночное небо с звездами и снегом",
        "image_path": os.path.join(BASE_DIR, "templates", "card3.png"),
        "font": {
            "path": os.path.join(BASE_DIR, "fonts", "festive.ttf"),
            "size": 42,  # ИСПРАВЛЕНО: был 300 (слишком большой!)
            "color": "white"
        },
        "text_position": {
            "x": "center",
            "y": 300,
            "max_width": 500,
            "line_height": 55
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

            # Загружаем шрифты
            font_path = config["font"]["path"]
            if os.path.exists(font_path):
                font_cache[template_id] = ImageFont.truetype(
                    font_path,
                    config["font"]["size"]
                )
                logger.info(f"✓ Loaded font: {template_id}")
            else:
                # Fallback на системный шрифт
                try:
                    font_cache[template_id] = ImageFont.truetype("arial.ttf", config["font"]["size"])
                    logger.info(f"✓ Using fallback font for: {template_id}")
                except:
                    font_cache[template_id] = ImageFont.load_default()
                    logger.warning(f"⚠ Using default font for: {template_id}")

        except Exception as e:
            logger.error(f"Error loading {template_id}: {e}")

    logger.info("Resources loaded!")


# Создаем Reply-клавиатуру
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎨 Создать открытку")],
        [KeyboardButton(text="👀 Посмотреть шаблоны"), KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)


# /start — приветствие
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = """
🎄 *Привет! Я бот для создания новогодних открыток!* 

Я помогу тебе создать красивую поздравительную открытку с твоим текстом. 

Выбери в меню ниже, что ты хочешь сделать:
    """
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )


# Обработка кнопки "Создать открытку"
@dp.message(F.text == "🎨 Создать открытку")
async def create_new_card(message: types.Message):
    # ДИНАМИЧЕСКИ создаем кнопки из конфига шаблонов
    keyboard_buttons = []
    for template_id, config in TEMPLATE_CONFIGS.items():
        keyboard_buttons.append([InlineKeyboardButton(
            text=config["name"],
            callback_data=template_id
        )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer(
        "Отлично! Выбери шаблон для своей открытки:",
        reply_markup=keyboard
    )


# Обработка выбора шаблона
@dp.callback_query(F.data.in_(TEMPLATE_CONFIGS.keys()))
async def process_template(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    template_id = callback_query.data
    user_templates[user_id] = template_id

    config = TEMPLATE_CONFIGS[template_id]

    await callback_query.message.answer(
        f"✨ Отлично! Выбран шаблон: *{config['name']}*\n\n"
        f"Теперь напиши текст, который хочешь разместить на открытке.\n"
        f"Например: *«С Новым Годом! Желаю счастья!»* 🌟",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )
    await callback_query.answer()


# СИНХРОННАЯ функция создания карточки (для вызова в отдельном потоке)
def create_card_sync(template_id, text):
    try:
        config = TEMPLATE_CONFIGS[template_id]

        # Используем кэшированные ресурсы
        if template_id not in template_cache:
            # Если нет в кэше, загружаем
            if not os.path.exists(config["image_path"]):
                raise FileNotFoundError(f"Template image not found: {config['image_path']}")
            template_cache[template_id] = Image.open(config["image_path"])

        img = template_cache[template_id].copy()  # Клонируем шаблон
        draw = ImageDraw.Draw(img)

        # Получаем шрифт из кэша или используем fallback
        font = font_cache.get(template_id)
        if font is None:
            try:
                font = ImageFont.truetype("arial.ttf", config["font"]["size"])
            except:
                font = ImageFont.load_default()

        # Обработка переноса текста с учетом конфига
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

        # Рисуем текст с учетом позиционирования из конфига
        y_position = position_config["y"]
        line_height = position_config["line_height"]

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]

            # Позиционирование по X из конфига
            if position_config["x"] == "center":
                x_position = (img.width - text_width) // 2
            else:
                x_position = position_config["x"]

            # Цвет текста из конфига
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


# АСИНХРОННАЯ обертка
async def create_card_with_config(template_id, text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        thread_pool,
        lambda: create_card_sync(template_id, text)
    )


# Просмотр шаблонов (ИСПРАВЛЕНО: убрал лишние символы)
@dp.message(F.text == "👀 Посмотреть шаблоны")
async def show_templates(message: types.Message):
    try:
        templates_info = "📋 *Доступные шаблоны:*\n\n"

        # ДИНАМИЧЕСКИ показываем информацию о шаблонах из конфига
        for template_id, config in TEMPLATE_CONFIGS.items():
            templates_info += f"*{config['name']}*\n"
            templates_info += f"{config['description']}\n\n"

        templates_info += "Хочешь создать открытку? Нажми «🎨 Создать открытку»!"

        await message.answer(templates_info, parse_mode="Markdown")

        # Показываем превью шаблонов
        for template_id, config in TEMPLATE_CONFIGS.items():
            if os.path.exists(config["image_path"]):
                with open(config["image_path"], "rb") as f:
                    photo = BufferedInputFile(f.read(), filename=f"{template_id}.png")
                    await message.answer_photo(
                        photo=photo,
                        caption=f"{config['name']}\n{config['description']}"
                    )

    except Exception as e:
        logger.error(f"Error showing templates: {e}")
        await message.answer("❌ Не удалось загрузить шаблоны")


# Помощь
@dp.message(F.text == "ℹ️ Помощь")
async def show_help(message: types.Message):
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
    await message.answer(help_text, parse_mode="Markdown")


# Обработка текста и создание открытки
@dp.message(F.text)
async def create_card(message: types.Message):
    user_id = message.from_user.id

    # Пропускаем команды меню
    if message.text in ["🎨 Создать открытку", "👀 Посмотреть шаблоны", "ℹ️ Помощь"]:
        return

    # Проверяем, что пользователь выбрал шаблон
    if user_id not in user_templates:
        await message.answer(
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
        processing_msg = await message.answer("🔄 Создаю открытку...")

        # Используем оптимизированную функцию
        output = await create_card_with_config(template_id, message.text)

        photo = BufferedInputFile(output.getvalue(), filename="card.png")

        # Удаляем сообщение "Создаю..."
        await processing_msg.delete()

        # Отправляем готовую открытку
        await message.answer_photo(
            photo=photo,
            caption="🎉 *Готово! Твоя открытка создана!*\n\n"
                    "Можешь отправить её друзьям или создать ещё одну через меню ниже!",
            parse_mode="Markdown",
            reply_markup=main_keyboard
        )

    except Exception as e:
        logger.error(f"Error creating card: {e}")
        await message.answer(
            "❌ Произошла ошибка при создании открытки. Попробуй еще раз.",
            reply_markup=main_keyboard
        )

    finally:
        # Удаляем выбор шаблона после отправки
        if user_id in user_templates:
            del user_templates[user_id]


# Добавляем команду для просмотра шаблонов
@dp.message(Command("show_templates"))
async def show_templates_command(message: types.Message):
    await show_templates(message)


# Функция для запуска бота
async def main():
    # Предзагружаем ресурсы
    load_resources()

    logger.info("🤖 Bot started!")
    await dp.start_polling(bot)


# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        thread_pool.shutdown()