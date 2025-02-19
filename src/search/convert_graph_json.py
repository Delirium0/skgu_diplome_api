import json

from src.search.main import coords_floor1_5_building, floor_images_5_building
from src.search.main import graph_5_building


# Функция для определения типа узла по его имени
def determine_node_type(node_name):
    if "office" in node_name:
        return "office"
    elif "corridor" in node_name:
        return "corridor"
    else:
        return node_name  # либо можно вернуть "other"


# Функция преобразования в формат JSON для конкретного этажа
def convert_to_json(coords, graph, image_path):
    # Формирование словаря узлов
    nodes = {}
    for node, (x, y) in coords.items():
        node_type = determine_node_type(node)
        nodes[node] = [x, y, node_type]

    # Формирование списка рёбер.
    # Ребро добавляем, если оба узла присутствуют в coords.
    # Для избежания дубликатов используем set с нормализованным ключом.
    edges_set = set()
    edges = []
    for src, neighbors in graph.items():
        if src not in coords:
            continue
        for neighbor, weight in neighbors:
            if neighbor not in coords:
                continue
            # Для неориентированного графа нормализуем ключ ребра
            edge_key = tuple(sorted([src, neighbor]))
            if edge_key not in edges_set:
                edges_set.add(edge_key)
                edges.append([src, neighbor, float(weight)])

    # Собираем итоговую структуру
    json_data = {
        "image_path": image_path,
        "nodes": nodes,
        "edges": edges
    }
    return json_data


# Преобразуем для первого этажа
json_floor1 = convert_to_json(coords_floor1_5_building, graph_5_building, floor_images_5_building["1"])

# Преобразуем для второго этажа


# Сохраняем полученные JSON-структуры в файлы
with open("old/floor1_building_5.json", "w", encoding="utf-8") as f:
    json.dump(json_floor1, f, indent=4, ensure_ascii=False)


print("JSON-файлы успешно созданы!")
