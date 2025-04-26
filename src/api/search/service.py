import base64
import io # <-- Добавлен io
import math # <-- Добавлен math
import os # os больше не нужен для путей, но может использоваться где-то еще
from typing import Dict, Any, List

from fastapi import HTTPException
from PIL import Image, ImageDraw # <-- Добавлены импорты PIL

# --- Ваши импорты (оставляем как есть) ---
try:
    from src.api.search.route.formating import format_location_info
    from src.api.search.database.models import Node, Edge
    from src.api.search.database.search_repo import map_repository
    from src.api.search.route.search_route import dijkstra_path, build_graph
    # Убираем импорт оригинальной draw_path_with_arrows, т.к. используем новую
    # from src.api.search.route.search_route import draw_path_with_arrows
except ImportError as e:
    print(f"ОШИБКА ИМПОРТА: {e}")
    # Добавьте заглушки или обработку ошибок, если нужно
    Node = Edge = object
    map_repository = None
    dijkstra_path = build_graph = format_location_info = lambda *args, **kwargs: None

# --- ВСТАВЛЯЕМ КОД НОВОЙ ФУНКЦИИ draw_path_with_arrows_to_buffer ---
# (Код этой функции приведен выше в Шаге 1)
def draw_path_with_arrows_to_buffer(image_data_b64: str, floor_nodes: Dict[str, Node], path: List[str]) -> io.BytesIO:
    """
    Рисует путь (линии) и СТРЕЛКИ НА ПОВОРОТАХ на изображении этажа
    и возвращает результат в виде io.BytesIO.
    """
    if not Image or not ImageDraw:
        raise RuntimeError("Библиотека Pillow (PIL) не установлена или не импортирована.")

    img = None
    try:
        img_bytes = base64.b64decode(image_data_b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        draw = ImageDraw.Draw(img)
    except Exception as e:
        print(f"Ошибка загрузки изображения из base64: {e}")
        raise ValueError(f"Не удалось загрузить изображение этажа: {e}")

    path_coordinates = []
    for node_name in path:
        node = floor_nodes.get(node_name)
        if node and hasattr(node, 'x') and hasattr(node, 'y') and \
           isinstance(node.x, (int, float)) and isinstance(node.y, (int, float)):
            path_coordinates.append((int(node.x), int(node.y)))
        else:
            print(f"Предупреждение: Узел '{node_name}' не найден или не имеет координат x/y.")

    if len(path_coordinates) > 1:
        try:
            draw.line(path_coordinates, fill="red", width=5, joint="curve")
            for i in range(len(path_coordinates) - 1):
                p1 = path_coordinates[i]
                p2 = path_coordinates[i+1]
                if p1 == p2: continue
                angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
                arrow_length = 15
                arrow_angle_degrees = 30
                arrow_angle_rad = math.radians(arrow_angle_degrees)
                ax = p2[0] - arrow_length * math.cos(angle - arrow_angle_rad)
                ay = p2[1] - arrow_length * math.sin(angle - arrow_angle_rad)
                bx = p2[0] - arrow_length * math.cos(angle + arrow_angle_rad)
                by = p2[1] - arrow_length * math.sin(angle + arrow_angle_rad)
                draw.polygon([(int(ax), int(ay)), (int(bx), int(by)), p2], fill="red", outline="red")
        except Exception as e:
            print(f"Ошибка при рисовании пути/стрелок: {e}")

    buffer = io.BytesIO()
    try:
        img.save(buffer, format="PNG")
        buffer.seek(0)
    except Exception as e:
        print(f"Ошибка сохранения изображения в буфер: {e}")
        raise
    finally:
        if img: img.close()
    return buffer
# --- КОНЕЦ НОВОЙ ФУНКЦИИ ---


# --- Ваша функция get_route_suggestions (с минимальными изменениями) ---
async def get_route_suggestions(start: str, target: str, building: str, language: str = "ru") -> Dict[str, Any]:
    """
    Возвращает путь между двумя локациями в здании, с изображениями для каждого этажа.
    Использует `language` для отображения информации о локациях.
    **Изменено: Рисует в память.**
    """
    if map_repository is None: raise HTTPException(status_code=503, detail="Сервис базы данных недоступен.")
    if not dijkstra_path or not build_graph: raise HTTPException(status_code=503, detail="Компоненты поиска пути недоступны.")
    if not format_location_info: print("Предупреждение: Функция format_location_info недоступна.")

    print(f"[Suggest Route] Target Query: {target}, Building: {building}")
    try:
        nodes = await map_repository.search_nodes(target)
        if not nodes:
             raise HTTPException(status_code=404, detail=f"Локации по запросу '{target}' не найдены.")

        # Проверяем, что у найденного узла есть имя
        first_node = nodes[0]
        if not isinstance(first_node, Node) or not hasattr(first_node, 'name'):
             raise HTTPException(status_code=500, detail="Некорректные данные найденной локации.")

        actual_target = first_node.name # Берем имя первого узла как цель
        print(f"[Suggest Route] Using actual target: {actual_target}")

        # 1. Получаем список всех этажей для данного здания
        floors = await map_repository.get_all_floors_by_building(building)
        location = await map_repository.get_location_by_building(building)

        location_info = format_location_info(location) if location and format_location_info else None # Добавил проверку
        if not floors:
            raise HTTPException(status_code=404, detail="Данных для выбранного здания не найдено")

        # 2. Собираем данные графа (узлы и ребра)
        all_nodes: Dict[str, Node] = {}
        all_edges: List[Edge] = []
        floor_mapping: Dict[str, int] = {}  # node_name -> floor_number
        image_paths: Dict[int, str] = {}  # floor_number -> image_data (base64)

        for floor in floors:
             # Добавим проверки на floor
            if not hasattr(floor, 'id') or not hasattr(floor, 'floor_number') or not hasattr(floor, 'image_data'):
                 print(f"Предупреждение: Пропуск этажа с неполными данными: {floor}")
                 continue
            floor_nodes = await map_repository.get_nodes_by_floor_id(floor.id)
            floor_edges = await map_repository.get_edges_by_floor_id(floor.id)

            for node in floor_nodes:
                 # Добавим проверки на node
                if not isinstance(node, Node) or not hasattr(node, 'name'): continue
                all_nodes[node.name] = node
                floor_mapping[node.name] = floor.floor_number

            all_edges.extend(edge for edge in floor_edges if isinstance(edge, Edge)) # Добавим проверку типа ребра
            image_paths[floor.floor_number] = floor.image_data

        # Проверка на наличие start и actual_target в собранных узлах
        if start not in all_nodes: raise HTTPException(status_code=404, detail=f"Стартовый узел '{start}' не найден на карте.")
        if actual_target not in all_nodes: raise HTTPException(status_code=404, detail=f"Целевой узел '{actual_target}' (из поиска '{target}') не найден на карте.")

        # 3. Строим граф
        graph = build_graph(all_nodes, all_edges)

        # 4. Вычисляем путь
        path = dijkstra_path(graph, start, actual_target) # Используем actual_target
        if not path:
            # Добавим больше деталей в ошибку
            start_floor = floor_mapping.get(start, 'неизвестен')
            target_floor = floor_mapping.get(actual_target, 'неизвестен')
            raise HTTPException(status_code=404, detail=f"Путь от '{start}'(эт.{start_floor}) до '{actual_target}'(эт.{target_floor}) не найден.")

        # 5. Группируем путь по этажам
        floor_paths: Dict[int, List[str]] = {}
        for node_name in path:
            floor_number = floor_mapping.get(node_name)
            # Добавим проверку
            if floor_number is None:
                print(f"Ошибка: узел '{node_name}' из пути не найден в floor_mapping!")
                continue
            floor_paths.setdefault(floor_number, []).append(node_name)

        # 6. Генерируем изображения для каждого этажа (ИСПОЛЬЗУЯ ПАМЯТЬ)
        images = []
        for floor_number, floor_path_nodes in floor_paths.items(): # Переименовал floor_path в floor_path_nodes
            image_data_b64 = image_paths.get(floor_number)
            if not image_data_b64:
                print(f"Предупреждение: Нет image_data для floor_number {floor_number}")
                continue

            # Получаем Node объекты ТОЛЬКО для текущего этажа
            current_floor_nodes = {name: node for name, node in all_nodes.items() if floor_mapping.get(name) == floor_number}

            # --- ИЗМЕНЕНИЕ: Рисуем в буфер ---
            try:
                image_buffer = draw_path_with_arrows_to_buffer(image_data_b64, current_floor_nodes, floor_path_nodes)
                img_bytes = image_buffer.read()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                image_buffer.close() # Закрываем буфер
            except Exception as e:
                 print(f"Ошибка при генерации изображения для этажа {floor_number}: {e}")
                 # Можно пропустить этаж или вернуть ошибку 500
                 continue
            # --- КОНЕЦ ИЗМЕНЕНИЯ ---

            # Получаем имена для локаций на данном этаже на нужном языке
            floor_location_names: Dict[str, str] = {}
            for node_name, node in current_floor_nodes.items():
                # Добавим проверку типа
                if not isinstance(node, Node): continue

                if language == "ru": name = node.name_ru or node.name_en or node.name_kz or node.name or "N/A"
                elif language == "en": name = node.name_en or node.name_ru or node.name_kz or node.name or "N/A"
                elif language == "kz": name = node.name_kz or node.name_ru or node.name_en or node.name or "N/A"
                else: name = node.name_ru or node.name_en or node.name_kz or node.name or "N/A"
                floor_location_names[node_name] = name

            images.append({"floor": floor_number, "image": img_b64, "location_names": floor_location_names})

        return {"images": images, "location": location_info}

    except HTTPException as e:
        raise e # Пробрасываем HTTP ошибки
    except Exception as e:
        # Ловим другие возможные ошибки (БД, PIL, ...)
        print(f"Непредвиденная ошибка в get_route_suggestions: {e}")
        import traceback
        traceback.print_exc() # Печатаем полный стек для отладки
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при обработке запроса маршрута по подсказке.")


# --- Ваша функция get_route (с минимальными изменениями) ---
async def get_route(start: str, target: str, building: str, language: str = "ru") -> Dict[str, Any]:
    """
    Возвращает путь между двумя локациями в здании, с изображениями для каждого этажа.
    Использует `language` для отображения информации о локациях.
    **Изменено: Рисует в память.**
    """
    # (Начало функции идентично get_route_suggestions: проверки импортов, шаги 1 и 2 - сбор данных)
    if map_repository is None: raise HTTPException(status_code=503, detail="Сервис базы данных недоступен.")
    if not dijkstra_path or not build_graph: raise HTTPException(status_code=503, detail="Компоненты поиска пути недоступны.")
    if not format_location_info: print("Предупреждение: Функция format_location_info недоступна.")

    print(f"[Direct Route] Start: {start}, Target: {target}, Building: {building}")
    try:
        # 1. Получаем список всех этажей для данного здания
        floors = await map_repository.get_all_floors_by_building(building)
        location = await map_repository.get_location_by_building(building)

        location_info = format_location_info(location) if location and format_location_info else None
        if not floors:
            raise HTTPException(status_code=404, detail="Данных для выбранного здания не найдено")

        # 2. Собираем данные графа (узлы и ребра) - КОД ИДЕНТИЧЕН get_route_suggestions
        all_nodes: Dict[str, Node] = {}
        all_edges: List[Edge] = []
        floor_mapping: Dict[str, int] = {}
        image_paths: Dict[int, str] = {}

        for floor in floors:
            if not hasattr(floor, 'id') or not hasattr(floor, 'floor_number') or not hasattr(floor, 'image_data'): continue
            floor_nodes = await map_repository.get_nodes_by_floor_id(floor.id)
            floor_edges = await map_repository.get_edges_by_floor_id(floor.id)
            for node in floor_nodes:
                if not isinstance(node, Node) or not hasattr(node, 'name'): continue
                all_nodes[node.name] = node
                floor_mapping[node.name] = floor.floor_number
            all_edges.extend(edge for edge in floor_edges if isinstance(edge, Edge))
            image_paths[floor.floor_number] = floor.image_data

        # Проверка на наличие start и target (переданного напрямую)
        if start not in all_nodes: raise HTTPException(status_code=404, detail=f"Стартовый узел '{start}' не найден на карте.")
        if target not in all_nodes: raise HTTPException(status_code=404, detail=f"Целевой узел '{target}' не найден на карте.")

        # 3. Строим граф
        graph = build_graph(all_nodes, all_edges)

        # 4. Вычисляем путь
        path = dijkstra_path(graph, start, target) # Используем target напрямую
        if not path:
            start_floor = floor_mapping.get(start, 'неизвестен')
            target_floor = floor_mapping.get(target, 'неизвестен')
            raise HTTPException(status_code=404, detail=f"Путь от '{start}'(эт.{start_floor}) до '{target}'(эт.{target_floor}) не найден.")
        print(f"[Direct Route] Path found: {path}")

        # 5. Группируем путь по этажам - КОД ИДЕНТИЧЕН get_route_suggestions
        floor_paths: Dict[int, List[str]] = {}
        for node_name in path:
            floor_number = floor_mapping.get(node_name)
            if floor_number is None: continue
            floor_paths.setdefault(floor_number, []).append(node_name)

        # 6. Генерируем изображения для каждого этажа (ИСПОЛЬЗУЯ ПАМЯТЬ) - КОД ИДЕНТИЧЕН get_route_suggestions
        images = []
        for floor_number, floor_path_nodes in floor_paths.items():
            image_data_b64 = image_paths.get(floor_number)
            if not image_data_b64: continue
            current_floor_nodes = {name: node for name, node in all_nodes.items() if floor_mapping.get(name) == floor_number}

            # --- ИЗМЕНЕНИЕ: Рисуем в буфер ---
            try:
                image_buffer = draw_path_with_arrows_to_buffer(image_data_b64, current_floor_nodes, floor_path_nodes)
                img_bytes = image_buffer.read()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                image_buffer.close()
            except Exception as e:
                 print(f"Ошибка при генерации изображения для этажа {floor_number}: {e}")
                 continue
            # --- КОНЕЦ ИЗМЕНЕНИЯ ---

            floor_location_names: Dict[str, str] = {}
            for node_name, node in current_floor_nodes.items():
                if not isinstance(node, Node): continue
                if language == "ru": name = node.name_ru or node.name_en or node.name_kz or node.name or "N/A"
                elif language == "en": name = node.name_en or node.name_ru or node.name_kz or node.name or "N/A"
                elif language == "kz": name = node.name_kz or node.name_ru or node.name_en or node.name or "N/A"
                else: name = node.name_ru or node.name_en or node.name_kz or node.name or "N/A"
                floor_location_names[node_name] = name

            images.append({"floor": floor_number, "image": img_b64, "location_names": floor_location_names})

        return {"images": images, "location": location_info}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Непредвиденная ошибка в get_route: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при обработке запроса маршрута.")


# --- Ваша функция get_temps (переименована в get_location_suggestions для ясности) ---
async def get_location_suggestions(term: str, language: str = "ru") -> Dict[str, Any]:
    """
    Получает подсказки из базы данных на основе поискового запроса.
    (Функционально идентична вашей get_temps)
    """
    if map_repository is None: raise HTTPException(status_code=503, detail="Сервис базы данных недоступен.")

    print(f"[Suggest] Term: {term}, Lang: {language}")
    try:
        nodes = await map_repository.search_nodes(term)
    except Exception as e:
        print(f"Ошибка БД при поиске '{term}': {e}")
        raise HTTPException(status_code=500, detail="Ошибка поиска подсказок")

    suggestions = []
    for node in nodes:
        # Добавляем проверки типов и атрибутов
        if not isinstance(node, Node): continue
        building_number = None
        if hasattr(node, 'floor') and node.floor and hasattr(node.floor, 'building_number'):
             building_number = node.floor.building_number

        if language == "ru": name = node.name_ru or node.name_en or node.name_kz or node.name or "N/A"
        elif language == "en": name = node.name_en or node.name_ru or node.name_kz or node.name or "N/A"
        elif language == "kz": name = node.name_kz or node.name_ru or node.name_en or node.name or "N/A"
        else: name = node.name_ru or node.name_en or node.name_kz or node.name or "N/A"

        description = ""
        if language == "ru": description = node.description_ru or node.description_en or node.description_kz or ""
        elif language == "en": description = node.description_en or node.description_ru or node.description_kz or ""
        elif language == "kz": description = node.description_kz or node.description_ru or node.description_en or ""
        else: description = node.description_ru or node.description_en or node.description_kz or ""

        suggestion = {
            "id": node.name if hasattr(node, 'name') else None,
            "key": node.id if hasattr(node, 'id') else None,
            "name": name,
            "building_number": building_number,
            "building_name": "корпус",
            "description": description,
        }
        # Добавляем только валидные подсказки
        if suggestion["id"]:
             suggestions.append(suggestion)

    return {"suggestions": suggestions}