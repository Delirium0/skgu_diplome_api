import base64

from fastapi import HTTPException

from src.api.search.database.test_crud import get_location_names, get_graph, coords_floor1, coords_floor2
from src.api.search.route.search_route import dijkstra_path, draw_path_with_arrows


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


floor_images = {
    "1": r"E:\PycharmProjects\skgu_diplome_api\src\api\search\images\first_floor_6_housingtest.png",
    "2": r"E:\PycharmProjects\skgu_diplome_api\src\api\search\images\second_floor_6_housing.png",
}
floor_coords = {
    "1": coords_floor1,
    "2": coords_floor2,
}


async def get_route(start: str, target: str):
    """
    Принимает start и target (имена узлов, например, '1_entrance' и '2_office_225'),
    строит путь, разбивает его по этажам и возвращает изображения маршрута (в base64) для каждого этажа.
    """
    graph = get_graph
    print(target)
    path = dijkstra_path(graph, start, target)
    if not path:
        raise HTTPException(status_code=404, detail="Путь не найден")

    # Группируем узлы по этажам по префиксу (до знака '_')
    floors = {}
    for node in path:
        floor = node.split('_')[0]  # Например, '1' или '2'

        floors.setdefault(floor, []).append(node)

    # Для каждого этажа генерируем картинку маршрута
    images = []
    for floor, floor_path in floors.items():
        # Берём исходное изображение и координаты для этажа
        image_path = floor_images.get(floor)
        coords = floor_coords.get(floor)
        if image_path is None or coords is None:
            continue

        # Отрисовываем весь путь, но на изображении будут видны только узлы, присутствующие в coords
        out_path = f"temp_{floor}.png"
        draw_path_with_arrows(image_path, coords, path, out_path)

        # Читаем картинку и конвертируем в base64
        with open(out_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append({"floor": floor, "image": img_b64})

    return {"path": path, "images": images}
