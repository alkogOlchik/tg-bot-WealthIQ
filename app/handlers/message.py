from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import bot, TEMPLATE_CONFIGS, user_templates, logger, get_main_keyboard
from app.services.image import create_card_sync
import os

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🎄 Привет! В этом боте ты можешь сделать персонализированные новогодние открытки для своих клиентов. Выбери шаблон, потом отправь текст и получи открытку! Лучше в тексте указать имя и отчество клиента, чтобы получилось адресно.

Выбери в меню ниже, что ты хочешь сделать:
    """
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "Создать открытку")
def create_new_card(message):
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

@bot.message_handler(func=lambda message: message.text == "Посмотреть шаблоны")
def show_templates(message):
    try:
        templates_info = "*Доступные шаблоны:*\n\n"

        for template_id, config in TEMPLATE_CONFIGS.items():
            templates_info += f"*{config['name']}*\n"
            templates_info += f"{config['description']}\n\n"

        templates_info += "Хочешь создать открытку? Нажми «Создать открытку»!"

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

@bot.message_handler(func=lambda message: message.text == "Помощь")
def show_help(message):
    help_text = """
🤖 *Как пользоваться ботом:*

*🎨 Создать открытку:*
1. Нажми «Создать открытку»
2. Выбери понравившийся шаблон
3. Напиши текст поздравления  
4. Получи готовую открытку!

*Приятного творчества!* ✨
    """
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id

    # Пропускаем команды меню
    if message.text in ["Создать открытку", "Посмотреть шаблоны", "Помощь"]:
        return

    # Проверяем, что пользователь выбрал шаблон
    if user_id not in user_templates:
        bot.send_message(
            message.chat.id,
            "Чтобы создать открытку, сначала выбери шаблон — нажми «Создать открытку»",
            reply_markup=get_main_keyboard()
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
            caption="🎉 *Готово! Отправляй клиенту и возвращайся за новой открыткой.*\n\n",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

    except Exception as e:
        logger.error(f"Error creating card: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при создании открытки. Попробуй еще раз.",
            reply_markup=get_main_keyboard()
        )

    finally:
        # Удаляем выбор шаблона после отправки
        if user_id in user_templates:
            del user_templates[user_id]