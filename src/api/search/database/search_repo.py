import base64
import heapq
import math
import os
from typing import List, Dict, Any, Optional

from PIL import Image, ImageDraw
from fastapi import HTTPException
from sqlalchemy import select

from config import DATABASE_URL
from src.api.search.database.models import Floor, Node, Edge
from src.database.singleton_database import DatabaseSingleton

DEBUG_SHOW_NODES = True


class MapRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def get_floor_by_building_and_floor_number(self, building_number: str, floor_number: int) -> Optional[Floor]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Floor).where(Floor.building_number == building_number, Floor.floor_number == floor_number)
            )
            return result.scalars().first()

    async def get_nodes_by_floor_id(self, floor_id: int) -> List[Node]:
        async with self.db.session_maker() as session:
            result = await session.execute(select(Node).where(Node.floor_id == floor_id))
            return result.scalars().all()

    async def get_edges_by_floor_id(self, floor_id: int) -> List[Edge]:
        async with self.db.session_maker() as session:
            result = await session.execute(select(Edge).where(Edge.floor_id == floor_id))
            return result.scalars().all()

    async def get_all_floors_by_building(self, building_number: str) -> List[Floor]:
        async with self.db.session_maker() as session:
            result = await session.execute(select(Floor).where(Floor.building_number == building_number))
            return result.scalars().all()

    async def get_node_by_name_and_floor_id(self, node_name: str, floor_id: int) -> Optional[Node]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Node).where(Node.name == node_name, Node.floor_id == floor_id)
            )
            return result.scalars().first()


# Вспомогательные функции (перемещены для ясности)
def build_graph(nodes: Dict[str, Node], edges: List[Edge]) -> Dict[str, List[tuple[str, float]]]:
    """Строит граф на основе узлов и ребер."""
    graph = {node_name: [] for node_name in nodes}
    for edge in edges:
        graph[edge.source_node_name].append((edge.target_node_name, edge.weight or 1.0))  # Вес по умолчанию = 1
        graph[edge.target_node_name].append((edge.source_node_name, edge.weight or 1.0))  # Граф неориентированный
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
    if DEBUG_SHOW_NODES:
        for node_name, node in coords_dict.items():  # Получаем объект Node
            x = node.x
            y = node.y
            r = 4  # радиус кружка
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            draw.text((x + 5, y - 5), node_name, fill='blue')

    # Сохраняем изображение
    img.save(out_path)


import io


# Эндпоинт
async def get_route(start: str, target: str, building: str, language: str = "ru") -> Dict[str, Any]:
    """
    Возвращает путь между двумя локациями в здании, с изображениями для каждого этажа.
    Использует `language` для отображения информации о локациях.
    """
    map_repository = MapRepository()

    # 1. Получаем список всех этажей для данного здания
    floors = await map_repository.get_all_floors_by_building(building)
    if not floors:
        raise HTTPException(status_code=404, detail="Данных для выбранного здания не найдено")

    # 2. Собираем данные графа (узлы и ребра)
    all_nodes: Dict[str, Node] = {}
    all_edges: List[Edge] = []
    floor_mapping: Dict[str, str] = {}  # node_name -> floor_id
    image_paths: Dict[int, str] = {}  # floor_id -> image_data (base64)

    for floor in floors:
        floor_nodes = await map_repository.get_nodes_by_floor_id(floor.id)
        floor_edges = await map_repository.get_edges_by_floor_id(floor.id)

        for node in floor_nodes:
            all_nodes[node.name] = node
            floor_mapping[node.name] = floor.id  # Сопоставляем node name с floor id

        all_edges.extend(floor_edges)
        image_paths[floor.id] = floor.image_data  # Сопоставляем floor id с image data

    # 3. Строим граф
    graph = build_graph(all_nodes, all_edges)

    # 4. Вычисляем путь
    path = dijkstra_path(graph, start, target)
    if not path:
        raise HTTPException(status_code=404, detail="Путь не найден")

    # 5. Группируем путь по этажам
    floor_paths: Dict[int, List[str]] = {}  # floor_id -> list of node names
    for node_name in path:
        floor_id = floor_mapping[node_name]
        floor_paths.setdefault(floor_id, []).append(node_name)

    # 6. Генерируем изображения для каждого этажа
    images = []
    for floor_id, floor_path in floor_paths.items():
        image_data = image_paths.get(floor_id)
        if not image_data:
            continue

        # Получаем Node объекты для текущего этажа (вместо словаря)
        floor_nodes = {node.name: node for node in all_nodes.values() if floor_mapping[node.name] == floor_id}

        # Создаем временный файл для изображения
        out_path = os.path.join(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\temp_files",
                                f"floor_{floor_id}_path.png")  # Добавляем ".png"

        draw_path_with_arrows(image_data, floor_nodes, floor_path, out_path)

        with open(out_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        # Получаем имена для локаций на данном этаже на нужном языке
        floor_location_names: Dict[str, str] = {}
        for node_name, node in floor_nodes.items():
            if language == "ru":
                floor_location_names[node_name] = node.name_ru or node.name_en or node.name_kz or "N/A"
            elif language == "en":
                floor_location_names[node_name] = node.name_en or node.name_ru or node.name_kz or "N/A"
            elif language == "kz":
                floor_location_names[node_name] = node.name_kz or node.name_ru or node.name_en or "N/A"
            else:
                floor_location_names[node_name] = node.name_ru or node.name_en or node.name_kz or "N/A"

        images.append({"floor": floor_id, "image": img_b64, "location_names": floor_location_names})

    return {"path": path, "images": images}
