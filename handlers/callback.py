from telebot.types import ForceReply
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


@bot.callback_query_handler(func=lambda call: call.data in TEMPLATE_CONFIGS.keys())
def process_template(call):
    user_id = call.from_user.id
    template_id = call.data
    user_templates[user_id] = template_id

    config = TEMPLATE_CONFIGS[template_id]
    language = config.get("language", "ru")

    if language == "en":
        message_text = (
            f"Отлично! Выбрана открытка: *{config['name']}*\n\n"
            "Теперь напиши текст, который хочешь разместить на открытке.\n"
            "Например, “Ivan Ivanovich, wishing you a New Year filled with light, clarity, and moments that truly inspire.”"
        )
    else:
        message_text = (
            f"Отлично! Выбрана открытка: *{config['name']}*\n\n"
            "Теперь напиши текст, который хочешь разместить на открытке.\n"
            "Например, «Иван Иванович, пусть 2026 принесет Вам радость, вдохновение и только приятные сюрпризы!»\n\n"
            "Или нажми «Выбрать текстовку»."
        )

    bot.send_message(
        call.message.chat.id,
        message_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("text_template:"))
def process_text_template(call):
    user_id = call.from_user.id
    payload = call.data.split("text_template:")[-1]

    if payload == "custom":
        bot.send_message(
            call.message.chat.id,
            "Напиши свою текстовку в чате, когда будешь готов. Мы сможем сделать открытку, как только выберешь шаблон и отправишь текст.",
            reply_markup=get_main_keyboard()
        )
        bot.answer_callback_query(call.id, "Вводи свой текст")
        return

    try:
        language, text_id = payload.split(":")
    except ValueError:
        bot.answer_callback_query(call.id, "Не удалось распознать текстовку")
        return

    template = _get_text_config(language, text_id)

    if not template:
        bot.answer_callback_query(call.id, "Не удалось найти текстовку")
        return

    selected_template = user_templates.get(user_id)

    if template.get("requires_name", False):
        pending_text_templates[user_id] = {
            "text_id": text_id,
            "language": language,
            "template_id": selected_template
        }
        if language == "ru":
            prompt = "Как зовут клиента? Подставлю имя и сразу соберу открытку."
            placeholder = "Например, Иван Иванович"
        else:
            prompt = "Как зовут клиента? Подставлю имя и сразу соберу открытку."
            placeholder = "e.g. Ivan Smith"
        bot.send_message(
            call.message.chat.id,
            prompt,
            reply_markup=ForceReply(
                input_field_placeholder=placeholder
            )
        )
        bot.answer_callback_query(call.id, f"Текстовка «{template['title']}»")
        return

    bot.send_message(call.message.chat.id, "Собираю открытку с выбранным текстом 👇")
    generate_card(
        call.message.chat.id,
        user_id,
        template["text"],
        template_id=selected_template
    )
    bot.answer_callback_query(call.id, f"Текстовка «{template['title']}»")


def _get_text_pool(language):
    return TEXT_TEMPLATES if language == "ru" else ENG_TEXT_TEMPLATES


def _get_text_config(language, text_id):
    return _get_text_pool(language).get(text_id)