from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot, TEMPLATE_CONFIGS, user_templates, logger, get_main_keyboard


@bot.callback_query_handler(func=lambda call: call.data in TEMPLATE_CONFIGS.keys())
def process_template(call):
    user_id = call.from_user.id
    template_id = call.data
    user_templates[user_id] = template_id

    config = TEMPLATE_CONFIGS[template_id]

    bot.send_message(
        call.message.chat.id,
        f"Отлично! Выбран шаблон: *{config['name']}*\n\n"
        f"Теперь напиши текст, который хочешь разместить на открытке.\n"
        f"Например, «Иван Иванович, пусть 2026 принесет Вам радость, вдохновение и только приятные сюрпризы!»",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    bot.answer_callback_query(call.id)