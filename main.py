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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7997248089:AAFPNCq42ZsC7yGLydXG5KS5CBPbjIzZL5Q"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для хранения выбранного шаблона каждым пользователем
user_templates = {}

# Создаем Reply-клавиатуру (появляется там где обычно прикрепляют файлы)
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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎄 Шаблон 1 - Елочка", callback_data="template_1")],
            [InlineKeyboardButton(text="❄️ Шаблон 2 - Снежок", callback_data="template_2")]
        ]
    )
    await message.answer(
        "Отлично! Выбери шаблон для своей открытки:",
        reply_markup=keyboard
    )


# Обработка выбора шаблона
@dp.callback_query(F.data.startswith("template_"))
async def process_template(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_templates[user_id] = callback_query.data

    template_name = "🎄 Елочка" if callback_query.data == "template_1" else "❄️ Снежок"
    await callback_query.message.answer(
        f"✨ Отлично! Выбран шаблон: *{template_name}*\n\n"
        f"Теперь напиши текст, который хочешь разместить на открытке.\n"
        f"Например: *«С Новым Годом! Желаю счастья!»* 🌟",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )
    await callback_query.answer()


# Просмотр шаблонов
@dp.message(F.text == "👀 Посмотреть шаблоны")
async def show_templates(message: types.Message):
    try:
        templates_info = """
📋 *Доступные шаблоны:*

*🎄 Шаблон 1 - Елочка*
Классическая новогодняя открытка с елкой и украшениями

*❄️ Шаблон 2 - Снежок* 
Зимний пейзаж с снежинками и праздничной атмосферой

Хочешь создать открытку? Нажми «🎨 Создать открытку»!
        """
        await message.answer(templates_info, parse_mode="Markdown")

        # Показываем превью шаблонов если файлы существуют
        if os.path.exists("templates/card1.png"):
            with open("templates/card1.png", "rb") as f1:
                photo1 = BufferedInputFile(f1.read(), filename="template1.png")
                await message.answer_photo(
                    photo=photo1,
                    caption="🎄 Шаблон 1 - Елочка"
                )

        if os.path.exists("templates/card2.png"):
            with open("templates/card2.png", "rb") as f2:
                photo2 = BufferedInputFile(f2.read(), filename="template2.png")
                await message.answer_photo(
                    photo=photo2,
                    caption="❄️ Шаблон 2 - Снежок"
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

*👀 Посмотреть шаблоны:*
- Посмотри все доступные шаблоны перед созданием

*📌 Советы:*
- Текст лучше писать короткий и ёмкий
- Можно использовать эмодзи 🎄⭐️🎁
- Открытку можно отправить друзьям прямо из Telegram

*Команды:*
/start - показать это меню
/show_templates - посмотреть шаблоны

*Приятного творчества!* 🎨✨
    """
    await message.answer(help_text, parse_mode="Markdown")


# Обработка текста и создание открытки
@dp.message(F.text)
async def create_card(message: types.Message):
    user_id = message.from_user.id

    # Пропускаем команды меню (они уже обработаны выше)
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
        # Определяем, какой шаблон выбрал пользователь
        template_name = user_templates[user_id]
        template_path = "templates/card1.png" if template_name == "template_1" else "templates/card2.png"

        # Проверяем существование файла шаблона
        if not os.path.exists(template_path):
            await message.answer("❌ Файл шаблона не найден. Обратитесь к администратору.")
            logger.error(f"Template file not found: {template_path}")
            return

        # Загружаем шаблон
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)

        # Подключаем шрифт с обработкой ошибок
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "festive.ttf")

        # Проверяем существование шрифта
        if not os.path.exists(font_path):
            # Используем стандартный шрифт если festive.ttf не найден
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
                logger.warning("Using default font - arial.ttf not available")
        else:
            font = ImageFont.truetype(font_path, 40)

        # Наносим текст с базовой обработкой переноса
        text = message.text
        # Простой перенос текста
        max_width = img.width - 200  # Отступы по бокам
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

        # Рисуем текст построчно
        y_position = 200
        line_height = 50

        for line in lines:
            # Центрируем текст
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_position = (img.width - text_width) // 2

            draw.text((x_position, y_position), line, font=font, fill="white")
            y_position += line_height

        # Сохраняем в память
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)

        # Используем BufferedInputFile вместо InputFile
        photo = BufferedInputFile(output.getvalue(), filename="card.png")

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
        # Удаляем выбор шаблона после отправки (даже если была ошибка)
        if user_id in user_templates:
            del user_templates[user_id]


# Добавляем команду для просмотра шаблонов
@dp.message(Command("show_templates"))
async def show_templates_command(message: types.Message):
    await show_templates(message)


async def main():
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())