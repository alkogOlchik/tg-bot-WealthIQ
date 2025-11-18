import os
from PIL import ImageFont
from app.config import TEMPLATE_CONFIGS, font_path, logger


def calculate_font_size(text, template_id, draw=None, test_font=None):
    """
    Умный расчет размера шрифта с учетом:
    - Длины текста и количества строк
    - Ширины и высоты доступной области
    - Плотности символов (ширина разных символов)
    - Оптимальной читаемости
    """
    config = TEMPLATE_CONFIGS[template_id]
    position_config = config["text_position"]

    # Если есть draw и test_font, используем точный расчет
    if draw and test_font:
        return calculate_font_size_precise(text, template_id, draw, test_font)

    # Умный расчет на основе множества факторов
    base_font_size = config["font"]["size"]
    max_width = position_config["max_width"]
    max_height = position_config.get("max_height", 400)
    line_height_ratio = position_config.get("line_height_ratio", 1.3)

    text_length = len(text)

    # Фактор плотности текста (учитывает широкие/узкие символы)
    density_factor = calculate_text_density(text)

    # Фактор количества строк (предварительная оценка)
    estimated_lines = estimate_line_count(text, text_length, max_width, base_font_size)

    # Фактор важности шаблона (некоторые шаблоны требуют большего/меньшего текста)
    template_priority = get_template_priority(template_id)

    # Комплексный расчет с учетом всех факторов
    if text_length <= 10:
        # Очень короткий текст - можно использовать большой размер
        font_size = base_font_size * min(1.2, template_priority)

    elif text_length <= 20:
        # Короткие поздравления
        base_factor = 0.9
        lines_factor = max(0.7, 1.0 - (estimated_lines - 1) * 0.15)
        font_size = base_font_size * base_factor * lines_factor * density_factor * template_priority

    elif text_length <= 40:
        # Средние тексты
        base_factor = 0.75
        lines_factor = max(0.6, 1.0 - (estimated_lines - 1) * 0.2)
        font_size = base_font_size * base_factor * lines_factor * density_factor * template_priority

    elif text_length <= 60:
        # Длинные тексты
        base_factor = 0.6
        lines_factor = max(0.5, 1.0 - (estimated_lines - 1) * 0.25)
        font_size = base_font_size * base_factor * lines_factor * density_factor * template_priority

    else:
        # Очень длинные тексты
        base_factor = 0.45
        lines_factor = max(0.4, 1.0 - (estimated_lines - 1) * 0.3)
        font_size = base_font_size * base_factor * lines_factor * density_factor * template_priority

    # Гарантируем минимальный и максимальный размер
    min_font_size = position_config.get("min_font_size", 12)
    max_font_size = position_config.get("max_font_size", base_font_size * 1.5)

    font_size = max(min_font_size, min(max_font_size, int(font_size)))

    logger.info(f"📐 Smart font calculation: text='{text[:20]}...', length={text_length}, "
                f"estimated_lines={estimated_lines}, density={density_factor:.2f}, "
                f"final_size={font_size}")

    return font_size


def calculate_text_density(text):
    """
    Рассчитывает плотность текста (1.0 - средняя плотность)
    >1.0 - плотный текст (много узких символов)
    <1.0 - разреженный текст (много широких символов)
    """
    if not text:
        return 1.0

    # Широкие символы (занимают больше места)
    wide_chars = "MWQmwqАБВГДЖЗИЙКЛНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    # Узкие символы (занимают меньше места)
    narrow_chars = "il1|!.,:;'\"` I"
    # Средние символы (базовые)
    medium_chars = "abcdefghjknopqrstuvxyzABCDEFGHJKLMNOPQRSTUVXYZ0123456789"

    wide_count = sum(1 for char in text if char in wide_chars)
    narrow_count = sum(1 for char in text if char in narrow_chars)
    medium_count = sum(1 for char in text if char in medium_chars)
    total_chars = len(text)

    if total_chars == 0:
        return 1.0

    # Взвешенная плотность
    wide_ratio = wide_count / total_chars * 0.4  # широкие символы увеличивают размер
    narrow_ratio = narrow_count / total_chars * 0.3  # узкие символы уменьшают размер
    medium_ratio = medium_count / total_chars * 0.1  # средние почти не влияют

    density = 0.8 + wide_ratio - narrow_ratio + medium_ratio
    return max(0.5, min(1.5, density))  # ограничиваем диапазон


def estimate_line_count(text, text_length, max_width, base_font_size):
    """
    Оценивает количество строк на основе эвристик
    """
    # Средняя ширина символа в пикселях (приблизительно)
    avg_char_width = base_font_size * 0.6

    # Ориентировочное количество символов в строке
    chars_per_line = max_width / avg_char_width if avg_char_width > 0 else 30

    if chars_per_line <= 0:
        return 1

    estimated_lines = max(1, text_length / chars_per_line)

    # Учитываем принудительные переносы строк
    actual_newlines = text.count('\n') + 1
    estimated_lines = max(estimated_lines, actual_newlines)

    return int(estimated_lines) + 1  # +1 для запаса


def get_template_priority(template_id):
    """
    Возвращает коэффициент важности текста для разных шаблонов
    """
    template_priorities = {
        "template_1": 1.0,  # стандартный приоритет
        "template_2": 0.9,  # меньше текста (икра - маленькая область)
        "template_3": 1.1  # больше текста (леденец - большая область)
    }
    return template_priorities.get(template_id, 1.0)


def calculate_font_size_precise(text, template_id, draw, test_font):
    """
    Точный расчет размера шрифта через итеративное тестирование
    Использует бинарный поиск для нахождения оптимального размера
    """
    config = TEMPLATE_CONFIGS[template_id]
    position_config = config["text_position"]
    max_width = position_config["max_width"]
    max_height = position_config.get("max_height", 400)
    line_height = position_config["line_height"]

    # Начинаем с базового размера
    base_font_size = config["font"]["size"]
    min_size = position_config.get("min_font_size", 12)
    max_size = position_config.get("max_font_size", base_font_size * 2)

    # Бинарный поиск оптимального размера
    low, high = min_size, max_size
    best_size = base_font_size

    for iteration in range(8):  # максимум 8 итераций
        if low > high:
            break

        current_size = (low + high) // 2
        try:
            # Создаем временный шрифт для тестирования
            temp_font = ImageFont.truetype(font_path, current_size)

            # Разбиваем текст на строки
            lines = wrap_text_to_fit(draw, text, temp_font, max_width)

            # Проверяем влезает ли по высоте
            total_height = len(lines) * line_height

            if total_height <= max_height and all_lines_fit(draw, lines, temp_font, max_width):
                # Текст влезает, пробуем увеличить размер
                best_size = current_size
                low = current_size + 1
            else:
                # Текст не влезает, уменьшаем размер
                high = current_size - 1

        except Exception as e:
            # Если ошибка шрифта, уменьшаем размер
            logger.warning(f"Font error at size {current_size}: {e}")
            high = current_size - 1

    logger.info(f"🎯 Precise font calculation: {best_size}px for '{text[:15]}...' (after {iteration} iterations)")
    return best_size


def wrap_text_to_fit(draw, text, font, max_width):
    """Разбивает текст на строки чтобы влезал в максимальную ширину"""
    words = text.split()
    if not words:
        return []

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


def all_lines_fit(draw, lines, font, max_width):
    """Проверяет что все строки влезают в максимальную ширину"""
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width > max_width:
            return False
    return True


def get_dynamic_font(template_id, text, draw=None):
    """
    Получает оптимальный шрифт для текста и шаблона
    """
    config = TEMPLATE_CONFIGS[template_id]
    font_path = config["font"]["path"]

    if not os.path.exists(font_path):
        logger.error(f"✗ Font file not found: {font_path}")
        raise FileNotFoundError(f"Font file not found: {font_path}")

    # Если передан draw, используем точный расчет
    if draw:
        font_size = calculate_font_size_precise(text, template_id, draw, font_path)
    else:
        font_size = calculate_font_size(text, template_id)

    try:
        font = ImageFont.truetype(font_path, font_size)
        logger.info(f"✓ Loaded font: {font_path}, size: {font_size}")
        return font
    except Exception as e:
        logger.error(f"✗ Failed to load font {font_path}: {e}")
        raise Exception(f"Could not load font {font_path}: {e}")