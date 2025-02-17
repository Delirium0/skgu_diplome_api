import heapq
from collections import deque

import math
from PIL import Image, ImageDraw
import heapq
import math
from collections import deque

from PIL import Image, ImageDraw


# --- Функции поиска пути ---
def bfs_path(graph, start, goal):
    visited = set([start])
    queue = deque([(start, [start])])
    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        for neighbor, _ in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def dijkstra_path(graph, start, goal):
    queue = [(0, start, [start])]
    seen = {start: 0}
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node == goal:
            return path
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if neighbor not in seen or new_cost < seen[neighbor]:
                seen[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))
    return None


DEBUG_SHOW_NODES = True


# --- Функция отрисовки пути ---
def draw_path(image_path, coords_dict, path, out_path):
    """ Рисует маршрут (красная линия) и, если DEBUG включён, отображает узлы (синие кружки). """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    path_on_this_floor = [p for p in path if p in coords_dict]
    for i in range(len(path_on_this_floor) - 1):
        x1, y1 = coords_dict[path_on_this_floor[i]]
        x2, y2 = coords_dict[path_on_this_floor[i + 1]]
        draw.line((x1, y1, x2, y2), fill='red', width=3)
    if DEBUG_SHOW_NODES:
        for node, (x, y) in coords_dict.items():
            r = 4
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            draw.text((x + 5, y - 5), node, fill='blue')
    img.save(out_path)


def draw_path_with_arrows(image_path, coords_dict, path, out_path, arrow_length=10, arrow_angle=30):
    """
    Рисует маршрут с стрелками, указывающими направление.

    :param image_path: путь к исходному изображению
    :param coords_dict: словарь координат узлов
    :param path: список узлов пути
    :param out_path: путь для сохранения изображения
    :param arrow_length: длина стрелочных "крыльев" (в пикселях)
    :param arrow_angle: угол между линией и стрелочным крылом (в градусах)
    """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Отбираем только те точки, для которых есть координаты на данном этаже
    path_on_this_floor = [p for p in path if p in coords_dict]

    for i in range(len(path_on_this_floor) - 1):
        x1, y1 = coords_dict[path_on_this_floor[i]]
        x2, y2 = coords_dict[path_on_this_floor[i + 1]]

        # Рисуем основной сегмент пути (синяя линия)
        draw.line((x1, y1, x2, y2), fill=(27, 115, 244), width=3)

        # Вычисляем угол направления линии
        angle = math.atan2(y2 - y1, x2 - x1)
        rad_arrow_angle = math.radians(arrow_angle)

        # Вычисляем координаты для двух линий стрелки (от конца отрезка)
        arrow_point1 = (
            x2 - arrow_length * math.cos(angle - rad_arrow_angle),
            y2 - arrow_length * math.sin(angle - rad_arrow_angle)
        )
        arrow_point2 = (
            x2 - arrow_length * math.cos(angle + rad_arrow_angle),
            y2 - arrow_length * math.sin(angle + rad_arrow_angle)
        )

        # Рисуем линии стрелки
        draw.line((x2, y2, arrow_point1[0], arrow_point1[1]), fill=(27, 115, 244), width=3)
        draw.line((x2, y2, arrow_point2[0], arrow_point2[1]), fill=(27, 115, 244), width=3)

    # Если включён режим отладки, рисуем узлы и их подписи
    if DEBUG_SHOW_NODES:
        for node, (x, y) in coords_dict.items():
            r = 4  # радиус кружка
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            draw.text((x + 5, y - 5), node, fill='blue')

    img.save(out_path)
