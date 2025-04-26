import base64
import os
from typing import Dict, Any, List

from fastapi import HTTPException

from src.api.search.route.formating import format_location_info
from src.api.search.database.models import Node, Edge
from src.api.search.database.search_repo import map_repository
from src.api.search.route.search_route import dijkstra_path, build_graph, draw_path_with_arrows


async def get_route_suggestions(start: str, target: str, building: str, language: str = "ru") -> Dict[str, Any]:
    """
    Возвращает путь между двумя локациями в здании, с изображениями для каждого этажа.
    Использует `language` для отображения информации о локациях.
    """
    print(target)
    print(building)
    nodes = await map_repository.search_nodes(target)

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
    print(suggestions)
    target = suggestions[0].get('id')
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

async def get_route(start: str, target: str, building: str, language: str = "ru") -> Dict[str, Any]:
    """
    Возвращает путь между двумя локациями в здании, с изображениями для каждого этажа.
    Использует `language` для отображения информации о локациях.
    """

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
    print(path)
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
