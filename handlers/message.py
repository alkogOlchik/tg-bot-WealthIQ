from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from config import (
    bot,
    TEMPLATE_CONFIGS,
    TEXT_TEMPLATES,
    ENG_TEXT_TEMPLATES,
    user_templates,
    pending_text_templates,
    logger,
    get_main_keyboard
)
from handlers.common import generate_card
from services.image import load_resources
import os

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🎄 Привет! В этом боте ты можешь сделать персонализированные новогодние открытки для своих клиентов. Выбери шаблон, потом отправь боту текст поздравления и получи готовую открытку!
Лучше в тексте указать имя и отчество клиента. И лучше не писать много, достаточно одного предложения. Если не знаешь, что написать, нажми «Посмотреть текстовки».
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

@bot.message_handler(func=lambda message: message.text == "Выбрать текстовку")
def suggest_texts(message):
    user_id = message.from_user.id

    if user_id not in user_templates:
        bot.send_message(
            message.chat.id,
            "Сначала выбери шаблон открытки — нажми «Создать открытку», выбери вариант, а потом возвращайся к текстовкам.",
            reply_markup=get_main_keyboard()
        )
        return

    template_id = user_templates[user_id]
    template_config = TEMPLATE_CONFIGS.get(template_id)
    language = template_config.get("language", "ru") if template_config else "ru"
    text_pool = _get_text_pool(language)

    if not text_pool:
        bot.send_message(
            message.chat.id,
            "Для выбранного шаблона пока нет готовых текстовок. Напиши свой текст вручную.",
            reply_markup=get_main_keyboard()
        )
        return

    header = "Вот заготовки под этот шаблон. Выбери подходящую:"
    bot.send_message(message.chat.id, header)

    keyboard = InlineKeyboardMarkup(row_width=2)
    for idx, (text_id, config) in enumerate(text_pool.items(), start=1):
        preview_text = _preview_text(config, language)
        bot.send_message(message.chat.id, f"{idx}. {preview_text}")
        keyboard.add(InlineKeyboardButton(
            text=config.get("button_label", f"#{idx}"),
            callback_data=f"text_template:{language}:{text_id}"
        ))

    keyboard.add(InlineKeyboardButton(
        text="✍️ Свой текст",
        callback_data="text_template:custom"
    ))

    bot.send_message(
        message.chat.id,
        "Когда определишься, просто нажми на кнопку ниже:",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == "Посмотреть открытки")
def show_templates(message):
    try:
        templates_info = "*Доступные открытки:*\n\n"

        for template_id, config in TEMPLATE_CONFIGS.items():
            description = config.get("description", "")
            templates_info += f"*{config['name']}*\n"
            templates_info += f"{description}\n\n"

        templates_info += "Хочешь создать открытку? Нажми «Создать открытку»!"

        bot.send_message(message.chat.id, templates_info, parse_mode="Markdown")

        # Показываем превью шаблонов
        for template_id, config in TEMPLATE_CONFIGS.items():
            if os.path.exists(config["image_path"]):
                description = config.get("description", "— описание появится чуть позже —")
                with open(config["image_path"], "rb") as f:
                    bot.send_photo(
                        message.chat.id,
                        f,
                        caption=f"{config['name']}\n{description}"
                    )

    except Exception as e:
        logger.error(f"Error showing templates: {e}")
        bot.send_message(message.chat.id, "❌ Не удалось загрузить шаблоны")

@bot.message_handler(func=lambda message: message.text == "Помощь")
def show_help(message):
    help_text = """
Как пользоваться ботом:

1. Нажми «Создать открытку»
2. Выбери понравившийся шаблон
3. Напиши текст поздравления или нажми «Выбрать текстовку» и выбери вариант, а затем укажи имя клиента 
4. Получи готовую открытку!

    """
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id

    # Пропускаем команды меню
    if message.text in ["Создать открытку", "Выбрать текстовку", "Посмотреть открытки", "Помощь"]:
        return

    # Обработка ответа с именем для текстовки
    if user_id in pending_text_templates:
        pending_data = pending_text_templates.pop(user_id)
        language = pending_data.get("language", "ru")
        text_id = pending_data.get("text_id")
        template_id = pending_data.get("template_id")
        template = _get_text_config(language, text_id)

        if not template:
            bot.send_message(
                message.chat.id,
                "Не удалось подготовить текстовку. Попробуй выбрать её еще раз.",
                reply_markup=get_main_keyboard()
            )
            return

        name_value = message.text.strip()
        if not name_value:
            pending_text_templates[user_id] = pending_data
            placeholder = "Например, Иван Иванович" if language == "ru" else "e.g. Ivan Smith"
            error_message = (
                "Имя не может быть пустым. Напиши имя или имя и отчество клиента."
                if language == "ru"
                else "Name can't be empty. Please type your client's name."
            )
            bot.send_message(
                message.chat.id,
                error_message,
                reply_markup=ForceReply(input_field_placeholder=placeholder)
            )
            return

        final_text = template["text"].replace("{name}", name_value)

        confirmation_text = (
            "Подставил имя в текстовку и создаю открытку 👇"
            if language == "ru"
            else "Added the name to the greeting and creating the card 👇"
        )
        bot.send_message(message.chat.id, confirmation_text)
        generate_card(message.chat.id, user_id, final_text, template_id=template_id)
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

    generate_card(message.chat.id, user_id, message.text)


def _get_text_pool(language):
    return TEXT_TEMPLATES if language == "ru" else ENG_TEXT_TEMPLATES


def _get_text_config(language, text_id):
    return _get_text_pool(language).get(text_id)


def _preview_text(config, language):
    sample_name = "Иван Иванович" if language == "ru" else "Mary Smith"
    text = config["text"]
    if "{name}" in text:
        return text.replace("{name}", sample_name)
    return text