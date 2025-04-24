from PIL import Image, ImageDraw, ImageFont
import os
import sys

def draw_hatched_rect(draw, xy, line_color='black', hatch_spacing=6, line_width=1):
    """Вспомогательная функция для рисования заштрихованного прямоугольника."""
    x0, y0, x1, y1 = xy
    if x1 <= x0 or y1 <= y0: return # Проверка на вырожденный прямоугольник
    # Рисуем штриховку (диагональные линии)
    margin = 1 # Уменьшил отступ штриховки
    for i in range(int((x1 - x0) + (y1 - y0)), -int(x1-x0), -hatch_spacing): # Изменил условие остановки для полного покрытия
        start_x = max(x0, x0 + i - (y1 - y0))
        start_y = min(y1, y0 + i)
        end_x = min(x1, x0 + i)
        end_y = max(y0, y0 + i - (x1 - x0))

        # Обрезка линии точно по границам прямоугольника
        # Находим пересечения с границами y0, y1, x0, x1
        # Пересечение с y = y1: x = x0 + i - (y1 - y0)
        # Пересечение с x = x1: y = y0 + i - (x1 - x0)
        # Пересечение с y = y0: x = x0 + i - (y0 - y0) = x0 + i
        # Пересечение с x = x0: y = y0 + i - (x0 - x0) = y0 + i

        p1 = (start_x, start_y)
        p2 = (end_x, end_y)

        # Отсечение по верхней границе (y0)
        if p1[1] < y0: p1 = (p1[0] + (y0 - p1[1]), y0)
        if p2[1] < y0: p2 = (p2[0] + (y0 - p2[1]), y0)
        # Отсечение по нижней границе (y1)
        if p1[1] > y1: p1 = (p1[0] - (p1[1] - y1), y1)
        if p2[1] > y1: p2 = (p2[0] - (p2[1] - y1), y1)
        # Отсечение по левой границе (x0)
        if p1[0] < x0: p1 = (x0, p1[1] + (x0 - p1[0]))
        if p2[0] < x0: p2 = (x0, p2[1] + (x0 - p2[0]))
         # Отсечение по правой границе (x1)
        if p1[0] > x1: p1 = (x1, p1[1] - (p1[0] - x1))
        if p2[0] > x1: p2 = (x1, p2[1] - (p2[0] - x1))

        # Рисуем обрезанную линию, если она валидна
        if p1[0] <= x1 and p1[0] >= x0 and p1[1] <= y1 and p1[1] >= y0 and \
           p2[0] <= x1 and p2[0] >= x0 and p2[1] <= y1 and p2[1] >= y0 and \
           (abs(p1[0] - p2[0]) > 1 or abs(p1[1] - p2[1]) > 1) : # Проверка на точку
             draw.line([p1, p2], fill=line_color, width=line_width)


def draw_text_centered(draw, text, box, font, color='black'):
    """Рисует текст, центрированный внутри заданного прямоугольника box."""
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0: return
    try:
        # Используем bounding box самого текста для более точного центрирования
        left, top, right, bottom = font.getbbox(text, anchor='lt')
        text_width = right - left
        text_height = bottom - top
        # Вычисляем позицию верхнего левого угла текста для центрирования
        text_x = x0 + (x1 - x0 - text_width) / 2
        text_y = y0 + (y1 - y0 - text_height) / 2 - top # Коррекция на 'top' из getbbox
        draw.text((text_x, text_y), text, fill=color, font=font, anchor='lt')
    except AttributeError: # Если getbbox недоступен
         text_width, text_height = draw.textlength(text, font=font), 10 # Приблизительно
         text_x = x0 + (x1 - x0 - text_width) / 2
         text_y = y0 + (y1 - y0 - text_height) / 2
         draw.text((text_x, text_y), text, fill=color, font=font)
    except Exception as e:
        print(f"Warning: Text centering/drawing failed for '{text}' ({e}). Using fallback.")
        draw.text((x0 + 5, y0 + 5), text, fill=color, font=font)


# --- Параметры изображения ---
img_width = 800
img_height = 550 # Уменьшил обратно, т.к. нет нижних выступов как у V3
bg_color = 'white'
line_color = 'black'
line_width = 2
margin = 30 # Уменьшил общий отступ

# --- Создание изображения ---
img = Image.new('RGB', (img_width, img_height), bg_color)
draw = ImageDraw.Draw(img)

# --- Определение координат ---
content_width = img_width - 2 * margin
content_height_total = img_height - 2 * margin - 40 # Общая высота контента (с местом для заголовка)
corridor_height_ratio = 0.20 # Доля высоты коридора

# Y-координаты
y_title_bottom = margin + 40
y_top = y_title_bottom + 10
y_mid1 = y_top + (content_height_total * (1 - corridor_height_ratio) / 2) # Верхний край коридора
y_mid2 = y_mid1 + (content_height_total * corridor_height_ratio)       # Нижний край коридора
y_bottom = y_top + content_height_total                                # Низ основной части

# X-координаты
x_left = margin
x_right = x_left + content_width

# Деление верхнего ряда (4 комнаты: 2, 3, 4, 5) - примерно равные
x_div_top1 = x_left + content_width * 0.25
x_div_top2 = x_left + content_width * 0.50
x_div_top3 = x_left + content_width * 0.75

# Деление нижнего ряда (3 комнаты: 12, 11, 10) - 11 широкая
room_12_width_ratio = 0.22
room_10_width_ratio = 0.22
room_11_width_ratio = 1.0 - room_12_width_ratio - room_10_width_ratio

x_div_bot1 = x_left + content_width * room_12_width_ratio # Граница 12 | 11
x_div_bot2 = x_left + content_width * (room_12_width_ratio + room_11_width_ratio) # Граница 11 | 10

# Координаты для левого выхода/коридора
exit_corridor_width_ratio = 0.18
exit_corridor_height = y_mid2 - y_mid1 # Такой же высоты, как основной коридор
x_exit_end = x_left - content_width * exit_corridor_width_ratio
y_exit_top = y_mid1
y_exit_bottom = y_mid2

# Координаты для лестничных выступов (они не сильно выступают)
stair_ext_width_ratio = 0.03
x_left_stair_ext = x_left - content_width * stair_ext_width_ratio
x_right_stair_ext = x_right + content_width * stair_ext_width_ratio

# --- Рисование внешних стен ---
door_gap = 20 # Для верхних выходов

# Верхняя линия (с разрывами на выходы)
exit_top1_center = x_left + content_width * 0.375 # Центр между 2/3 и 3/4
exit_top2_center = x_left + content_width * 0.625 # Центр между 3/4 и 4/5
draw.line([(x_left, y_top), (exit_top1_center - door_gap / 2, y_top)], fill=line_color, width=line_width)
draw.line([(exit_top1_center + door_gap / 2, y_top), (exit_top2_center - door_gap / 2, y_top)], fill=line_color, width=line_width)
draw.line([(exit_top2_center + door_gap / 2, y_top), (x_right, y_top)], fill=line_color, width=line_width)

# Нижняя линия (с небольшими выступами под лестницы)
draw.line([(x_left, y_bottom), (x_left_stair_ext, y_bottom)], fill=line_color, width=line_width) # Левый выступ низ
draw.line([(x_left_stair_ext, y_bottom), (x_right_stair_ext, y_bottom)], fill=line_color, width=line_width) # Основной низ
draw.line([(x_right_stair_ext, y_bottom), (x_right, y_bottom)], fill=line_color, width=line_width) # Правый выступ низ

# Левая сторона (с разрывом на выходной коридор)
draw.line([(x_left, y_top), (x_left, y_exit_top)], fill=line_color, width=line_width) # Верхняя часть
draw.line([(x_left, y_exit_bottom), (x_left, y_bottom)], fill=line_color, width=line_width) # Нижняя часть
# Добавляем стену для небольшого левого выступа лестницы
draw.line([(x_left_stair_ext, y_bottom), (x_left_stair_ext, y_mid2)], fill=line_color, width=line_width) # Вертикаль выступа лестницы
draw.line([(x_left_stair_ext, y_mid2), (x_left, y_mid2)], fill=line_color, width=line_width) # Верхняя горизонталь выступа лестницы

# Правая сторона
draw.line([(x_right, y_top), (x_right, y_bottom)], fill=line_color, width=line_width)
# Добавляем стену для небольшого правого выступа лестницы
draw.line([(x_right_stair_ext, y_bottom), (x_right_stair_ext, y_mid2)], fill=line_color, width=line_width) # Вертикаль выступа лестницы
draw.line([(x_right_stair_ext, y_mid2), (x_right, y_mid2)], fill=line_color, width=line_width) # Верхняя горизонталь выступа лестницы

# --- Левый выходной коридор ---
draw.line([(x_left, y_exit_top), (x_exit_end, y_exit_top)], fill=line_color, width=line_width) # Верхняя стена
draw.line([(x_left, y_exit_bottom), (x_exit_end, y_exit_bottom)], fill=line_color, width=line_width) # Нижняя стена
draw.line([(x_exit_end, y_exit_top), (x_exit_end, y_exit_bottom)], fill=line_color, width=line_width) # Левая стена (торец)

# --- Рисование внутренних стен ---
# Верхний ряд
draw.line([(x_div_top1, y_top), (x_div_top1, y_mid1)], fill=line_color, width=line_width) # 2 | 3
draw.line([(x_div_top2, y_top), (x_div_top2, y_mid1)], fill=line_color, width=line_width) # 3 | 4
draw.line([(x_div_top3, y_top), (x_div_top3, y_mid1)], fill=line_color, width=line_width) # 4 | 5

# Нижний ряд
draw.line([(x_div_bot1, y_mid2), (x_div_bot1, y_bottom)], fill=line_color, width=line_width) # 12 | 11
draw.line([(x_div_bot2, y_mid2), (x_div_bot2, y_bottom)], fill=line_color, width=line_width) # 11 | 10

# --- Рисование коридора с дверными проемами ---
door_gap = 20 # Ширина проема
door_offset = 5 # Смещение

# Верхняя стена коридора (y_mid1)
draw.line([(x_left, y_mid1), (x_left + (x_div_top1 - x_left)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # До 2
draw.line([(x_left + (x_div_top1 - x_left)/2 + door_gap/2, y_mid1), (x_div_top1 + (x_div_top2 - x_div_top1)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # До 3
draw.line([(x_div_top1 + (x_div_top2 - x_div_top1)/2 + door_gap/2, y_mid1), (x_div_top2 + (x_div_top3 - x_div_top2)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # До 4
draw.line([(x_div_top2 + (x_div_top3 - x_div_top2)/2 + door_gap/2, y_mid1), (x_div_top3 + (x_right - x_div_top3)/2 - door_gap/2, y_mid1)], fill=line_color, width=line_width) # До 5
draw.line([(x_div_top3 + (x_right - x_div_top3)/2 + door_gap/2, y_mid1), (x_right, y_mid1)], fill=line_color, width=line_width) # После 5

# Нижняя стена коридора (y_mid2)
# Учитываем левый выступ лестницы
draw.line([(x_left_stair_ext, y_mid2), (x_left + (x_div_bot1 - x_left)/2 - door_gap/2, y_mid2)], fill=line_color, width=line_width) # От выступа до 12
draw.line([(x_left + (x_div_bot1 - x_left)/2 + door_gap/2, y_mid2), (x_div_bot1 + (x_div_bot2 - x_div_bot1)/2 - door_gap/2, y_mid2)], fill=line_color, width=line_width) # До 11
draw.line([(x_div_bot1 + (x_div_bot2 - x_div_bot1)/2 + door_gap/2, y_mid2), (x_div_bot2 + (x_right - x_div_bot2)/2 - door_gap/2, y_mid2)], fill=line_color, width=line_width) # До 10
# Учитываем правый выступ лестницы
draw.line([(x_div_bot2 + (x_right - x_div_bot2)/2 + door_gap/2, y_mid2), (x_right_stair_ext, y_mid2)], fill=line_color, width=line_width) # До правого выступа

# --- Рисование лестниц (штриховка) ---
# Лестница слева (от коридора вниз в выступе)
draw_hatched_rect(draw, (x_left_stair_ext, y_mid2, x_div_bot1, y_bottom), line_color=line_color, line_width=1)
# Лестница справа (от коридора вниз в выступе)
draw_hatched_rect(draw, (x_div_bot2, y_mid2, x_right_stair_ext, y_bottom), line_color=line_color, line_width=1)


# --- Загрузка шрифта ---
# (Код загрузки шрифта без изменений)
font_path = None
font_size_room = 16
font_size_title = 24
font_names = ["arial.ttf", "verdana.ttf", "tahoma.ttf", "DejaVuSans.ttf", "calibri.ttf"]
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
        font_room = ImageFont.load_default(font_size_room)
        font_title = ImageFont.load_default(font_size_title)
except Exception as e:
    print(f"Error: Ошибка загрузки/использования шрифта ({e}). Используется встроенный шрифт PIL.")
    font_room = ImageFont.load_default()
    font_title = ImageFont.load_default()

# --- Добавление текста ---
# Верхний ряд
draw_text_centered(draw, "2", (x_left, y_top, x_div_top1, y_mid1), font_room)
draw_text_centered(draw, "3", (x_div_top1, y_top, x_div_top2, y_mid1), font_room)
draw_text_centered(draw, "4", (x_div_top2, y_top, x_div_top3, y_mid1), font_room)
draw_text_centered(draw, "5", (x_div_top3, y_top, x_right, y_mid1), font_room)

# Нижний ряд (области над лестницами для 10 и 12 не рисуем, только основную часть)
# Комната 12 (над лестницей) - текст помещаем в основной части здания, если есть место
# draw_text_centered(draw, "12", (x_left, y_mid2, x_div_bot1, y_bottom), font_room) # Вся область лестницы
draw_text_centered(draw, "11", (x_div_bot1, y_mid2, x_div_bot2, y_bottom), font_room) # Большая центральная комната
# Комната 10 (над лестницей)
# draw_text_centered(draw, "10", (x_div_bot2, y_mid2, x_right, y_bottom), font_room) # Вся область лестницы

# Текст для 10 и 12 нужно разместить аккуратнее, т.к. часть их площади - лестница
# Попробуем разместить их в верхней части их зон
room_12_text_box = (x_left, y_mid2, x_div_bot1, y_mid2 + (y_bottom - y_mid2) * 0.4) # Верхняя часть зоны 12
room_10_text_box = (x_div_bot2, y_mid2, x_right, y_mid2 + (y_bottom - y_mid2) * 0.4) # Верхняя часть зоны 10
draw_text_centered(draw, "12", room_12_text_box, font_room)
draw_text_centered(draw, "10", room_10_text_box, font_room)


# Заголовок
title_text = "Пристройка 1 этаж УК №6"
title_box = (margin, margin // 2, img_width - margin, y_title_bottom) # Область для заголовка
draw_text_centered(draw, title_text, title_box, font_title)


# --- Сохранение изображения ---
output_filename = "floor_plan_floor1_pil_style.png"
img.save(output_filename)
print(f"План этажа сохранен как '{output_filename}'")

# Показать изображение (опционально)
# try:
#     img.show()
# except Exception as e:
#     print(f"Не удалось показать изображение: {e}")