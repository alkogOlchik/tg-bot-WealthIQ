import os, io
import logging
from PIL import Image, ImageDraw, ImageFont
from config import TEMPLATE_CONFIGS, template_cache, logger
from services.fonts import get_dynamic_font, calculate_line_height


def create_card_sync(template_id, text):
    """
    Создает открытку с текстом на выбранном шаблоне
    """
    try:
        config = TEMPLATE_CONFIGS[template_id]

        # Используем кэшированные ресурсы
        if template_id not in template_cache:
            if not os.path.exists(config["image_path"]):
                raise FileNotFoundError(f"Template image not found: {config['image_path']}")
            template_cache[template_id] = Image.open(config["image_path"])

        img = template_cache[template_id].copy()
        draw = ImageDraw.Draw(img)

        # Сначала получаем временный шрифт для точного расчета
        temp_font_path = config["font"]["path"]
        temp_font = ImageFont.truetype(temp_font_path, 20)  # временный размер

        # Используем точный расчет с передачей draw
        font = get_dynamic_font(template_id, text, draw)
        # Обработка переноса текста
        lines = wrap_text(draw, text, font, config["text_position"]["max_width"])

        # Рисуем текст на изображении
        draw_text_on_image(draw, lines, font, config, img.height)

        # Сохраняем в память
        output = io.BytesIO()
        img.save(output, format="PNG", optimize=True)
        output.seek(0)

        return output

    except Exception as e:
        logger.error(f"Error in create_card_sync: {e}")
        raise


def wrap_text(draw, text, font, max_width):
    """
    Разбивает текст на строки согласно максимальной ширине
    """
    words = text.split()
    lines = []
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

    return lines


def draw_text_on_image(draw, lines, font, config, image_height):
    """
    Рисует текст на изображении с выравниванием по левому краю
    """
    position_config = config["text_position"]
    # Используем уменьшенный множитель для более плотного межстрочного интервала (было 2.0, стало 1.3)
    line_height = calculate_line_height(font.size, 1.3)

    # Рассчитываем общую высоту текстового блока
    total_text_height = len(lines) * line_height

    # Получаем область для текста из конфигурации
    text_area_y_start = position_config["y"]
    text_area_height = position_config.get("height", image_height - text_area_y_start)

    # Рассчитываем вертикальное центрирование
    y_start_position = text_area_y_start + (text_area_height - total_text_height) // 2

    # Выравнивание по левому краю - используем x_offset или x если это число
    x_config = position_config.get("x", "left")
    if isinstance(x_config, (int, float)):
        # Если x - это число, используем его как позицию
        x_position = x_config
    else:
        # Если x - это строка (left/center), используем x_offset или 0 по умолчанию
        x_position = position_config.get("x_offset", 0)

    # Рисуем текст с выравниванием по левому краю
    y_position = y_start_position

    for line in lines:
        draw.text((x_position, y_position), line, font=font, fill=config["font"]["color"])
        y_position += line_height


def load_resources():
    """
    Предзагружает шаблоны изображений в кэш
    """
    logger.info("Preloading resources...")

    for template_id, config in TEMPLATE_CONFIGS.items():
        try:
            image_path = config["image_path"]
            if os.path.exists(image_path):
                img = Image.open(image_path)
                template_cache[template_id] = img
                logger.info(f"✓ Loaded template: {template_id}")
            else:
                logger.error(f"✗ Missing template: {image_path}")

        except Exception as e:
            logger.error(f"Error loading {template_id}: {e}")

    logger.info("Resources loaded!")