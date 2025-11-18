import logging, telebot
from config import logger, bot
from services.image import load_resources
import handlers.message
import handlers.callback


if __name__ == "__main__":
    # Предзагружаем ресурсы
    load_resources()

    logger.info("Bot started!")

    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=30,
            skip_pending=True
        )
    except Exception as e:
        logger.error(f"Bot polling failed: {e}")
        print(f"Ошибка: {e}")