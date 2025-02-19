import math
from PIL import Image, ImageDraw
import json
import heapq
from collections import deque

# Константы отладки
DEBUG_SHOW_NODES = True

def load_graph_data(json_file):
    """Загружает данные графа из JSON-файла."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def build_graph(nodes, edges):
    """Строит граф на основе узлов и ребер."""
    graph = {}
    for node_name in nodes:
        graph[node_name] = []
    for node1, node2, weight in edges:
        print(node1, node2)
        graph[node1].append((node2, weight))
        graph[node2].append((node1, weight))
    return graph

# Функции поиска пути (BFS/Дейкстра и т.д.)
def bfs_path(graph, start, goal):
    """Поиск в ширину."""
    visited = set([start])
    queue = deque([(start, [start])])
    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        if current not in graph:
            continue
        for neighbor, _ in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def dijkstra_path(graph, start, goal):
    """Алгоритм Дейкстры."""
    if start not in graph or goal not in graph:
        return None
    queue = [(0, start, [start])]
    seen = {start: 0}
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node == goal:
            return path
        if node not in graph:
            continue
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if neighbor not in seen or new_cost < seen[neighbor]:
                seen[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))
    return None

# Функции для рисования маршрута
def draw_path_with_arrows(image_path, coords_dict, path, out_path, arrow_length=10, arrow_angle=30):
    """Рисует маршрут с стрелками."""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Отбираем только те точки, для которых есть координаты на данном этаже
    path_on_this_floor = [p for p in path if p in coords_dict]

    for i in range(len(path_on_this_floor) - 1):
        x1, y1, _ = coords_dict[path_on_this_floor[i]]  # Получаем координаты и тип узла
        x2, y2, _ = coords_dict[path_on_this_floor[i + 1]]

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
    if DEBUG_SHOW_NODES:
        for node, (x, y, _) in coords_dict.items(): # Получаем координаты и тип узла
            r = 4  # радиус кружка
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            draw.text((x + 5, y - 5), node, fill='blue')

    img.save(out_path)


def process_route(json_file, start_point, target_point, output_folder="path_images"):
    """
    Вычисляет путь и генерирует изображения маршрута, используя данные из JSON.
    """

    graph_data = load_graph_data(json_file)
    image_path = graph_data['image_path']  # Путь к изображению из JSON
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    graph = build_graph(nodes, edges)

    path = dijkstra_path(graph, start_point, target_point)
    print("Путь:", path)

    if not path:
        print("Путь не найден.")
        return

    # Извлекаем имя файла из пути к изображению
    image_filename = image_path.split("\\")[-1].split(".")[0]  # или os.path.basename(image_path)
    out_path = f'{output_folder}/{image_filename}_path.png'  # Путь для сохранения

    draw_path_with_arrows(image_path, nodes, path, out_path)


if __name__ == '__main__':
    json_file = r'E:\PycharmProjects\skgu_diplome_api\src\search\floor1_building1.json'
    start_point = '1_entrance'
    target_point = '2_office_214'
    process_route(json_file, start_point, target_point)