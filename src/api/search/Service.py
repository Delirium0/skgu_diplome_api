import os

from src.api.search.database.test_crud import get_location_names

import base64
import base64
from typing import Dict, Any

from fastapi import HTTPException

from src.api.search.database.test_crud import get_location_names
from src.search.merge_floors_json_search_paint import (
    load_graph_data,
    build_graph,
    draw_path_with_arrows,
    dijkstra_path
)


async def get_temps(term):
    suggestions = []
    for id_locations, name_ru in get_location_names.items():
        suggestion = {
            "id": id_locations,
            "name": name_ru,
            "building_number": "6",
            "building_name": "корпус",
            "description": "Кабинет изобразительного искусства"
        }
        suggestions.append(suggestion)

    filtered = [
        s
        for s in suggestions
        if term.lower() in s["name"].lower() or term.lower() in s["description"].lower()
    ]
    print(filtered)
    return {"suggestions": filtered}


JSON_FILES = [
    r'E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor1_building1.json',
    r'E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor2_building1.json',
    r'E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor1_building_5.json',
]


async def get_route(start: str, target: str, building: int = None,  language: str = "ru") -> Dict[str, Any]:
    """
    Возвращает путь между двумя локациями в здании, с изображениями для каждого этажа.
    Использует `language` для отображения информации о локациях.
    Если указан `building`, фильтрует результаты только для этого здания.
    """

    selected_files = [
        f for f in JSON_FILES
        if f.lower().find(f'building{building}') != -1 or f.lower().find(f'building_{building}') != -1
    ]
    print(selected_files)
    if not selected_files:
        raise HTTPException(status_code=404, detail="Данных для выбранного здания не найдено")

    graph_data = load_graph_data(selected_files)
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    image_paths = graph_data['image_paths']
    floor_mapping = graph_data['floor_mapping']

    graph = build_graph(nodes, edges)
    path = dijkstra_path(graph, start, target)

    if not path:
        raise HTTPException(status_code=404, detail="Путь не найден")

    floor_paths = {}
    for node in path:
        floor = floor_mapping[node]
        floor_paths.setdefault(floor, []).append(node)

    images = []
    for floor, floor_path in floor_paths.items():
        image_path = image_paths.get(floor)
        if not image_path:
            continue

        floor_nodes = {node: nodes[node] for node in nodes if floor_mapping[node] == floor}

        base_name = os.path.basename(image_path)  # Получаем имя файла изображения
        name_without_extension, _ = os.path.splitext(base_name)  # убираем расширение файла
        out_path = os.path.join(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\temp_files", f"{name_without_extension}_path.png")  # Добавляем ".png"
        print(out_path)
        draw_path_with_arrows(image_path, floor_nodes, floor_path, out_path)

        with open(out_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        # Получаем имена для локаций на данном этаже на нужном языке
        floor_location_names = {}
        for node_id in floor_nodes:
            node_data = floor_nodes[node_id]
            floor_location_names[node_id] = node_data['name'].get(language, node_data['name'].get("ru", "N/A"))

        images.append({"floor": floor, "image": img_b64, "location_names": floor_location_names})  # Добавляем имена

    return {"path": path, "images": images}
