from PIL import Image, ImageDraw, ImageFont
import os
import sys

def draw_hatched_rect(draw, xy, line_color='black', hatch_spacing=6, line_width=1): # Уменьшил spacing для плотности
    """Вспомогательная функция для рисования заштрихованного прямоугольника."""
    x0, y0, x1, y1 = xy
    # Рисуем контур прямоугольника (опционально, если он уже нарисован как часть стены)
    # draw.rectangle(xy, outline=line_color, width=line_width)
    # Рисуем штриховку (диагональные линии)
    for i in range(int((x1 - x0) + (y1 - y0)), 0, -hatch_spacing):
        start_x = max(x0, x0 + i - (y1 - y0))
        start_y = min(y1, y0 + i)
        end_x = min(x1, x0 + i)
        end_y = max(y0, y0 + i - (x1 - x0))
        # Добавим небольшие отступы, чтобы штриховка не касалась краев
        margin = 2
        if start_x < x1 - margin and start_y > y0 + margin and end_x > x0 + margin and end_y < y1 - margin:
             draw.line([(start_x, start_y), (end_x, end_y)], fill=line_color, width=line_width)


def draw_text_centered(draw, text, box, font, color='black'):
    """Рисует текст, центрированный внутри заданного прямоугольника box."""
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0: # Проверка на вырожденный прямоугольник
        print(f"Warning: Invalid box dimensions for text '{text}': {box}")
        return
    try:
        text_bbox = draw.textbbox((0, 0), text, font=font, anchor='lt')
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Предотвращаем деление на ноль или отрицательные размеры
        box_width = max(1, x1 - x0)
        box_height = max(1, y1 - y0)

        text_x = x0 + (box_width - text_width) / 2
        text_y = y0 + (box_height - text_height) / 2

        # Проверка, чтобы текст не выходил за границы (хотя бы частично)
        if text_x < x0: text_x = x0 + 2
        if text_y < y0: text_y = y0 + 2

        draw.text((text_x, text_y), text, fill=color, font=font, anchor='lt')

    except Exception as e:
        print(f"Warning: Text centering/drawing failed for '{text}' ({e}). Using fallback.")
        draw.text((x0 + 5, y0 + 5), text, fill=color, font=font)


# --- Параметры изображения ---
img_width = 800
img_height = 600 # Немного увеличил высоту для выступов
bg_color = 'white'
line_color = 'black'
line_width = 2
margin = 50

# --- Создание изображения ---
img = Image.new('RGB', (img_width, img_height), bg_color)
draw = ImageDraw.Draw(img)

# --- Определение координат ---
content_width = img_width - 2 * margin
content_height_main = (img_height - 2 * margin - 50) * 0.8 # Основная высота без нижних выступов
content_height_total = img_height - 2 * margin - 50 # Общая высота контента

# Y-координаты
y_title_bottom = margin + 40
y_top = y_title_bottom + 10
y_mid1 = y_top + content_height_main * 0.35 # Верхний край коридора
y_mid2 = y_top + content_height_main * 0.55 # Нижний край коридора
y_bottom_main = y_top + content_height_main # Низ основной части (до выступов)

# Координаты для комнаты 17A/17
y_mid3 = y_mid2 + (y_bottom_main - y_mid2) * 0.45 # Горизонтальная линия между 17A и 17

# Y-координаты для выступов и низа
y_bottom_ext_top = y_bottom_main # Верхняя граница выступов совпадает с низом основной части
y_bottom_ext = y_top + content_height_total # Низ выступов

# Основные X-координаты
x_left = margin
x_div1 = x_left + content_width * 0.18
x_div2 = x_left + content_width * 0.36
x_mid_indent_left = x_left + content_width * 0.45 # Левая граница центр. выступа (19)
x_mid_indent_right = x_left + content_width * 0.63 # Правая граница центр. выступа (19)
x_div3 = x_left + content_width * 0.54 # Используем для 14Г/16, но не для 20/19
x_div4 = x_left + content_width * 0.75 # Граница между 16/15 и 18/17A
x_right = x_left + content_width

# X-координаты для выступов
x_left_ext = x_left - content_width * 0.10 # Левый край левого выступа
x_right_ext = x_right + content_width * 0.10 # Правый край правого выступа

# --- Рисование внешних стен ---
# Верхняя линия
draw.line([(x_left, y_top), (x_right, y_top)], fill=line_color, width=line_width)
# Левая сторона
draw.line([(x_left, y_top), (x_left, y_bottom_main)], fill=line_color, width=line_width)
# Правая сторона
draw.line([(x_right, y_top), (x_right, y_bottom_main)], fill=line_color, width=line_width)

# --- Левый выступ и лестница ---
draw.line([(x_left, y_bottom_main), (x_left_ext, y_bottom_main)], fill=line_color, width=line_width) # Верх выступа
draw.line([(x_left_ext, y_bottom_main), (x_left_ext, y_bottom_ext)], fill=line_color, width=line_width) # Левая стена выступа
draw.line([(x_left_ext, y_bottom_ext), (x_left, y_bottom_ext)], fill=line_color, width=line_width) # Низ выступа
# Внутренняя (правая) стена выступа - не рисуем, это часть комнаты 21

# --- Правый выступ и лестница ---
draw.line([(x_right, y_bottom_main), (x_right_ext, y_bottom_main)], fill=line_color, width=line_width) # Верх выступа
draw.line([(x_right_ext, y_bottom_main), (x_right_ext, y_bottom_ext)], fill=line_color, width=line_width) # Правая стена выступа
draw.line([(x_right_ext, y_bottom_ext), (x_right, y_bottom_ext)], fill=line_color, width=line_width) # Низ выступа
# Внутренняя (левая) стена выступа - не рисуем, это часть комнат 17/17A

# --- Центральный выступ (под лестницу 19) ---
draw.line([(x_mid_indent_left, y_bottom_main), (x_mid_indent_left, y_bottom_ext)], fill=line_color, width=line_width) # Левая стена выступа
draw.line([(x_mid_indent_right, y_bottom_main), (x_mid_indent_right, y_bottom_ext)], fill=line_color, width=line_width) # Правая стена выступа
draw.line([(x_mid_indent_left, y_bottom_ext), (x_mid_indent_right, y_bottom_ext)], fill=line_color, width=line_width) # Низ выступа

# --- Нижняя линия основной части (между выступами) ---
draw.line([(x_left, y_bottom_ext), (x_mid_indent_left, y_bottom_ext)], fill=line_color, width=line_width) # Слева от центр. выступа
draw.line([(x_mid_indent_right, y_bottom_ext), (x_right, y_bottom_ext)], fill=line_color, width=line_width) # Справа от центр. выступа

# --- Рисование внутренних стен ---
# Верхний ряд
draw.line([(x_div1, y_top), (x_div1, y_mid1)], fill=line_color, width=line_width) # 14А | 14Б
draw.line([(x_div2, y_top), (x_div2, y_mid1)], fill=line_color, width=line_width) # 14Б | 14Г
draw.line([(x_div3, y_top), (x_div3, y_mid1)], fill=line_color, width=line_width) # 14Г | 16 (используем x_div3 здесь)
draw.line([(x_div4, y_top), (x_div4, y_mid1)], fill=line_color, width=line_width) # 16 | 15

# Нижний ряд
draw.line([(x_div2, y_mid2), (x_div2, y_bottom_main)], fill=line_color, width=line_width) # 21 | 20
# Стена 20 | Лестница 19 (левая стена центр. выступа) - уже нарисована как часть выступа
# Стена Лестница 19 | 18 (правая стена центр. выступа) - уже нарисована как часть выступа
draw.line([(x_div4, y_mid2), (x_div4, y_bottom_main)], fill=line_color, width=line_width) # 18 | 17A/17
# Разделитель 17A | 17
draw.line([(x_div4, y_mid3), (x_right, y_mid3)], fill=line_color, width=line_width)

# --- Рисование коридора с дверными проемами ---
door_gap = 20 # Увеличил ширину проема
door_offset = 5 # Небольшой отступ от угла для дверей

# Верхняя стена коридора (y_mid1)
draw.line([(x_left, y_mid1), (x_left + (x_div1 - x_left)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # Стена до двери 14А
draw.line([(x_left + (x_div1 - x_left)/2 + door_gap/2, y_mid1), (x_div1 + (x_div2 - x_div1)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # Стена до двери 14Б
draw.line([(x_div1 + (x_div2 - x_div1)/2 + door_gap/2, y_mid1), (x_div2 + (x_div3 - x_div2)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # Стена до двери 14Г
draw.line([(x_div2 + (x_div3 - x_div2)/2 + door_gap/2, y_mid1), (x_div3 + (x_div4 - x_div3)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # Стена до двери 16
draw.line([(x_div3 + (x_div4 - x_div3)/2 + door_gap/2, y_mid1), (x_div4 + door_offset - door_gap/2, y_mid1)], fill=line_color, width=line_width) # Стена до двери 15 (смещена влево)
draw.line([(x_div4 + door_offset + door_gap/2, y_mid1), (x_right, y_mid1)], fill=line_color, width=line_width) # Стена после двери 15

# Нижняя стена коридора (y_mid2)
draw.line([(x_left, y_mid2), (x_div2 - door_offset - door_gap/2, y_mid2)], fill=line_color, width=line_width) # Стена до двери 21 (смещена вправо)
draw.line([(x_div2 - door_offset + door_gap/2, y_mid2), (x_div2 + (x_mid_indent_left - x_div2)/2 - door_gap/2, y_mid2)], fill=line_color, width=line_width) # Стена до двери 20 (центр)
draw.line([(x_div2 + (x_mid_indent_left - x_div2)/2 + door_gap/2, y_mid2), (x_mid_indent_left, y_mid2)], fill=line_color, width=line_width) # Стена до лестницы 19 (нет двери, просто конец стены)
# ПРОЕМ ЛЕСТНИЦЫ 19 (от x_mid_indent_left до x_mid_indent_right) - стена не рисуется
draw.line([(x_mid_indent_right, y_mid2), (x_mid_indent_right + (x_div4 - x_mid_indent_right)/2 - door_gap/2, y_mid2)], fill=line_color, width=line_width) # Стена от лестницы 19 до двери 18 (центр)
draw.line([(x_mid_indent_right + (x_div4 - x_mid_indent_right)/2 + door_gap/2, y_mid2), (x_div4 + (x_right - x_div4)/2 - door_gap/2, y_mid2)], fill=line_color, width=line_width) # Стена до двери 17A/17 (центр проема)
draw.line([(x_div4 + (x_right - x_div4)/2 + door_gap/2, y_mid2), (x_right, y_mid2)], fill=line_color, width=line_width) # Стена после двери 17A/17

# --- Рисование лестниц (штриховка) ---
# Лестница слева (в выступе)
draw_hatched_rect(draw, (x_left_ext, y_bottom_main, x_left, y_bottom_ext), line_color=line_color, line_width=line_width)
# Лестница в центре (19 - заполняет свой выступ)
draw_hatched_rect(draw, (x_mid_indent_left, y_mid2, x_mid_indent_right, y_bottom_ext), line_color=line_color, line_width=line_width) # Начинается от коридора и идет до низа выступа
# Лестница справа (в выступе)
draw_hatched_rect(draw, (x_right, y_bottom_main, x_right_ext, y_bottom_ext), line_color=line_color, line_width=line_width)


# --- Загрузка шрифта ---
# (Код загрузки шрифта остается таким же)
font_path = None
font_size_room = 16 # Слегка уменьшил для 17А
font_size_title = 24
font_names = ["arial.ttf", "verdana.ttf", "tahoma.ttf", "DejaVuSans.ttf"]
search_paths = ["."]
if sys.platform == "win32":
    font_dir = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts")
    search_paths.append(font_dir)
elif sys.platform.startswith("linux"):
    search_paths.extend(["/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/truetype/msttcorefonts/", "/usr/share/fonts/truetype/liberation/", "/usr/share/fonts/TTF/"])
elif sys.platform == "darwin":
    search_paths.extend(["/System/Library/Fonts", "/Library/Fonts"])
for path_dir in search_paths:
    for name in font_names:
        potential_path = os.path.join(path_dir, name)
        if os.path.exists(potential_path):
            font_path = potential_path
            print(f"Используется шрифт: {font_path}")
            break
    if font_path: break
try:
    if font_path:
        font_room = ImageFont.truetype(font_path, font_size_room)
        font_title = ImageFont.truetype(font_path, font_size_title)
    else:
        print("Warning: Стандартные шрифты не найдены. Используется встроенный шрифт PIL.")
        font_room = ImageFont.load_default(font_size_room) # Попробуем задать размер для дефолтного
        font_title = ImageFont.load_default(font_size_title)
except Exception as e:
    print(f"Error: Ошибка загрузки/использования шрифта ({e}). Используется встроенный шрифт PIL.")
    font_room = ImageFont.load_default()
    font_title = ImageFont.load_default()


# --- Добавление текста ---
# Верхний ряд
draw_text_centered(draw, "14А", (x_left, y_top, x_div1, y_mid1), font_room)
draw_text_centered(draw, "14Б", (x_div1, y_top, x_div2, y_mid1), font_room)
draw_text_centered(draw, "14Г", (x_div2, y_top, x_div3, y_mid1), font_room)
draw_text_centered(draw, "16", (x_div3, y_top, x_div4, y_mid1), font_room)
draw_text_centered(draw, "15", (x_div4, y_top, x_right, y_mid1), font_room)

# Нижний ряд
draw_text_centered(draw, "21", (x_left, y_mid2, x_div2, y_bottom_main), font_room) # Граница y_bottom_main
draw_text_centered(draw, "20", (x_div2, y_mid2, x_mid_indent_left, y_bottom_main), font_room) # Граница y_bottom_main
# Комната 19 - это лестница, текст не добавляем
draw_text_centered(draw, "18", (x_mid_indent_right, y_mid2, x_div4, y_bottom_main), font_room) # Граница y_bottom_main
# Комната 17A
draw_text_centered(draw, "17A", (x_div4, y_mid2, x_right, y_mid3), font_room) # Верхняя часть
# Комната 17
draw_text_centered(draw, "17", (x_div4, y_mid3, x_right, y_bottom_main), font_room) # Нижняя часть

# Заголовок
title_text = "Пристройка 2 этаж УК №6"
title_box = (0, 0, img_width, y_title_bottom) # Область для заголовка
draw_text_centered(draw, title_text, title_box, font_title)


# --- Сохранение изображения ---
output_filename = "floor_plan_pil_style_v3.png"
img.save(output_filename)
print(f"План этажа сохранен как '{output_filename}'")

# Показать изображение (опционально)
# try:
#     img.show()
# except Exception as e:
#     print(f"Не удалось показать изображение: {e}")