import base64
import heapq
import io
import math
import os
from typing import List, Dict, Any, Optional

from PIL import Image, ImageDraw
from fastapi import HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.orm import joinedload, selectinload

from config import DATABASE_URL
from src.api.search.database.formating import format_location_info
from src.api.search.database.models import Floor, Node, Edge, Location
from src.database.singleton_database import DatabaseSingleton

DEBUG_SHOW_NODES = False


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

    async def get_location_by_building(self, building_number: str) -> Location:
        async with self.db.session_maker() as session:
            result = await session.execute(select(Location).join(Floor).where(Floor.building_number == building_number).options(selectinload(Location.bounds))
                                           )
            return result.scalar()

    async def get_node_by_name_and_floor_id(self, node_name: str, floor_id: int) -> Optional[Node]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Node).where(Node.name == node_name, Node.floor_id == floor_id)
            )
            return result.scalars().first()

    async def search_nodes(self, term: str) -> List[Node]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Node)
                .options(joinedload(Node.floor))  # Eagerly load the 'floor' relationship
                .where(
                    or_(
                        func.lower(Node.name_ru).contains(term.lower()),
                        func.lower(Node.name_en).contains(term.lower()),
                        func.lower(Node.name_kz).contains(term.lower()),
                        func.lower(Node.description_ru).contains(term.lower()),
                        func.lower(Node.description_en).contains(term.lower()),
                        func.lower(Node.description_kz).contains(term.lower())
                    ),
                    Node.type != "corridor"  # Исключаем узлы с типом "corridor"
                )
            )
            return result.scalars().all()


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
    if DEBUG_SHOW_NODES:
        for node_name, node in coords_dict.items():  # Получаем объект Node
            x = node.x
            y = node.y
            r = 4  # радиус кружка
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            draw.text((x + 5, y - 5), node_name, fill='blue')

    # Сохраняем изображение
    img.save(out_path)


# Эндпоинт для прокладывания маршрута
async def get_route(start: str, target: str, building: str, language: str = "ru") -> Dict[str, Any]:
    """
    Возвращает путь между двумя локациями в здании, с изображениями для каждого этажа.
    Использует `language` для отображения информации о локациях.
    """
    map_repository = MapRepository()

    # 1. Получаем список всех этажей для данного здания
    floors = await map_repository.get_all_floors_by_building(building)
    location = await map_repository.get_location_by_building(building)
    location_info = format_location_info(location)
    if not floors:
        raise HTTPException(status_code=404, detail="Данных для выбранного здания не найдено")
    # 2. Собираем данные графа (узлы и ребра)
    all_nodes: Dict[str, Node] = {}
    all_edges: List[Edge] = []
    floor_mapping: Dict[str, int] = {}  # node_name -> floor_number
    image_paths: Dict[int, str] = {}  # floor_number -> image_data (base64)

    for floor in floors:
        floor_nodes = await map_repository.get_nodes_by_floor_id(floor.id)
        floor_edges = await map_repository.get_edges_by_floor_id(floor.id)

        for node in floor_nodes:
            all_nodes[node.name] = node
            floor_mapping[node.name] = floor.floor_number  # Сопоставляем node name с floor number

        all_edges.extend(floor_edges)
        image_paths[floor.floor_number] = floor.image_data  # Сопоставляем floor number с image data

    # 3. Строим граф
    graph = build_graph(all_nodes, all_edges)

    # 4. Вычисляем путь
    path = dijkstra_path(graph, start, target)
    if not path:
        raise HTTPException(status_code=404, detail="Путь не найден")

    # 5. Группируем путь по этажам
    floor_paths: Dict[int, List[str]] = {}  # floor_number -> list of node names
    for node_name in path:
        floor_number = floor_mapping[node_name]
        floor_paths.setdefault(floor_number, []).append(node_name)

    # 6. Генерируем изображения для каждого этажа
    images = []
    for floor_number, floor_path in floor_paths.items():
        image_data = image_paths.get(floor_number)
        if not image_data:
            # print(f"Предупреждение: Нет image_data для floor_number {floor_number}")
            continue

        # Получаем floor_id, соответствующий floor_number (для floor_nodes)
        floor_id = next((floor.id for floor in floors if floor.floor_number == floor_number), None)
        if not floor_id:
            # print(f"Предупреждение: Нет floor_id для floor_number {floor_number}")
            continue

        # Получаем Node объекты для текущего этажа
        floor_nodes = {node.name: node for node in all_nodes.values() if floor_mapping.get(node.name) == floor_number}

        # Создаем временный файл для изображения
        out_path = os.path.join(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\temp_files",
                                f"floor_{floor_number}_path.png")

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

        images.append({"floor": floor_number, "image": img_b64, "location_names": floor_location_names})

    return {"images": images, "location": location_info}


async def get_temps(term: str, language: str = "ru") -> Dict[str, Any]:
    """
    Получает подсказки из базы данных на основе поискового запроса.
    """
    map_repository = MapRepository()
    nodes = await map_repository.search_nodes(term)

    suggestions = []
    for node in nodes:
        suggestion = {
            "id": node.name,
            "key": node.id,
            "name": node.name_ru or node.name_en or node.name_kz or node.name,
            "building_number": node.floor.building_number,
            "building_name": "корпус",
            "description": node.description_ru or node.description_en or node.description_kz or "",
        }
        suggestions.append(suggestion)

    return {"suggestions": suggestions}
