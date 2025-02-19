import base64

from fastapi import HTTPException

from src.api.search.database.test_crud import get_location_names, get_graph, coords_floor1, coords_floor2
from src.search.merge_floors_json_search_paint import load_graph_data, build_graph, draw_path_with_arrows, dijkstra_path


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
    r'E:\PycharmProjects\skgu_diplome_api\src\search\floor1_building1.json',
    r'E:\PycharmProjects\skgu_diplome_api\src\search\floor2_building1.json',
    r'E:\PycharmProjects\skgu_diplome_api\src\search\floor1_building_5.json'
    r'E:\PycharmProjects\skgu_diplome_api\src\search\qefqef.json'
]

import base64
from fastapi import HTTPException

from src.search.merge_floors_json_search_paint import (
    load_graph_data,
    build_graph,
    draw_path_with_arrows,
    dijkstra_path
)


async def get_route(start: str, target: str, building: int):
    """
    Принимает start и target (имена узлов, например, '1_entrance' и '2_office_222')
    и параметр building (номер здания, например, "1" или "5").

    Строит путь, разбивает его по этажам и возвращает изображения маршрута (в base64)
    только для выбранного здания.
    """
    # Фильтруем JSON-файлы по выбранному зданию.
    # Предполагается, что в имени файла содержится, например, "building1" или "building_5"

    selected_files = [
        f for f in JSON_FILES
        if f.lower().find(f'building{building}') != -1 or f.lower().find(f'building_{building}') != -1
    ]
    if building == 228:
        selected_files = [r'E:\PycharmProjects\skgu_diplome_api\src\search\qefqef.json']
    if not selected_files:
        raise HTTPException(status_code=404, detail="Данных для выбранного здания не найдено")
    print(selected_files)
    # Загружаем данные из выбранных JSON-файлов
    graph_data = load_graph_data(selected_files)
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    image_paths = graph_data['image_paths']
    floor_mapping = graph_data['floor_mapping']

    # Строим граф и ищем маршрут
    graph = build_graph(nodes, edges)
    path = dijkstra_path(graph, start, target)
    if not path:
        raise HTTPException(status_code=404, detail="Путь не найден")

    # Группируем узлы маршрута по этажам (floor_mapping содержит ключи, соответствующие имени файла)
    floor_paths = {}
    for node in path:
        floor = floor_mapping[node]
        floor_paths.setdefault(floor, []).append(node)

    # Для каждого этажа генерируем изображение маршрута
    images = []
    for floor, floor_path in floor_paths.items():
        image_path = image_paths.get(floor)
        if not image_path:
            continue

        # Формируем словарь узлов только для данного этажа
        floor_nodes = {node: nodes[node] for node in nodes if floor_mapping[node] == floor}
        out_path = f"temp_{floor}.png"
        draw_path_with_arrows(image_path, floor_nodes, floor_path, out_path)

        # Читаем сгенерированное изображение и кодируем в base64
        with open(out_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append({"floor": floor, "image": img_b64})

    return {"path": path, "images": images}
