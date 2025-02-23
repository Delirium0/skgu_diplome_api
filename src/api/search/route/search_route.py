import base64
import heapq
import io
import math
from typing import List, Dict

from PIL import Image, ImageDraw

from src.api.search.database.models import Node, Edge
from config import DEBUG


def build_graph(nodes: Dict[str, Node], edges: List[Edge]) -> Dict[str, List[tuple[str, float]]]:
    """Строит граф на основе узлов и ребер, пропуская ребра с отсутствующими узлами."""
    graph = {node_name: [] for node_name in nodes}
    for edge in edges:
        if edge.source_node_name not in graph:
            print(
                f"WARNING: Исходный узел '{edge.source_node_name}' не найден. Пропускаем ребро от '{edge.source_node_name}' к '{edge.target_node_name}'.")
            continue
        if edge.target_node_name not in graph:
            print(
                f"WARNING: Целевой узел '{edge.target_node_name}' не найден. Пропускаем ребро от '{edge.source_node_name}' к '{edge.target_node_name}'.")
            continue

        # Добавляем ребро в оба направления для неориентированного графа
        graph[edge.source_node_name].append((edge.target_node_name, edge.weight or 1.0))
        graph[edge.target_node_name].append((edge.source_node_name, edge.weight or 1.0))
    return graph


def dijkstra_path(graph: Dict[str, List[tuple[str, float]]], start: str, goal: str) -> List[str] | None:
    """Алгоритм Дейкстры."""
    if start not in graph or goal not in graph:
        return None

    queue = [(0, start, [start])]  # (cost, node, path)
    seen = {start: 0}  # {node: cost}

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


def draw_path_with_arrows(image_data: str, coords_dict: Dict[str, Node], path: List[str], out_path: str,
                          arrow_length=10, arrow_angle=30):
    """Рисует маршрут с стрелками."""
    # Декодируем Base64 изображение
    img_bytes = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(img_bytes))
    draw = ImageDraw.Draw(img)

    # Отбираем только те точки, для которых есть координаты на данном этаже
    path_on_this_floor = [p for p in path if p in coords_dict]

    for i in range(len(path_on_this_floor) - 1):
        node = coords_dict[path_on_this_floor[i]]  # Получаем объект Node
        x1 = node.x
        y1 = node.y

        node_next = coords_dict[path_on_this_floor[i + 1]]  # Для следующей точки
        x2 = node_next.x
        y2 = node_next.y

        # Рисуем основной сегмент пути (красная линия)
        draw.line((x1, y1, x2, y2), fill='red', width=3)

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
        draw.line((x2, y2, arrow_point1[0], arrow_point1[1]), fill='red', width=3)
        draw.line((x2, y2, arrow_point2[0], arrow_point2[1]), fill='red', width=3)

    # Если включён режим отладки, рисуем узлы и их подписи
    if DEBUG:
        for node_name, node in coords_dict.items():  # Получаем объект Node
            x = node.x
            y = node.y
            r = 4  # радиус кружка
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            draw.text((x + 5, y - 5), node_name, fill='blue')

    # Сохраняем изображение
    img.save(out_path)
