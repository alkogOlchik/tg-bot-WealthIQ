from config import bot, user_templates, logger, get_main_keyboard
from services.image import create_card_sync


def generate_card(chat_id, user_id, text, template_id=None):
    """
    Создает открытку с переданным текстом и отправляет пользователю.
    Возвращает True, если открытка отправлена, иначе False.
    """
    selected_template = template_id or user_templates.get(user_id)

    if not selected_template:
        bot.send_message(
            chat_id,
            "Сначала выбери шаблон — нажми «Создать открытку».",
            reply_markup=get_main_keyboard()
        )
        return False

    # Если шаблон получен извне (например, из pending state), синхронизируем хранение
    user_templates[user_id] = selected_template

    try:
        processing_msg = bot.send_message(chat_id, "🔄 Создаю открытку...")
        output = create_card_sync(selected_template, text)
        bot.delete_message(chat_id, processing_msg.message_id)

        bot.send_photo(
            chat_id,
            output,
            caption="🎉 *Готово! Отправляй клиенту и возвращайся за новой открыткой.*\n\n",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return True

    except Exception as exc:
        logger.error(f"Error creating card: {exc}")
        bot.send_message(
            chat_id,
            "❌ Произошла ошибка при создании открытки. Попробуй еще раз.",
            reply_markup=get_main_keyboard()
        )
        return False

    finally:
        user_templates.pop(user_id, None)

