import heapq
from collections import deque

from PIL import Image, ImageDraw

graph = {
    '1_entrance': [('1_corridor', 20)],
    '1_corridor': [
        ('1_corridor_104_archive', 1),
        ('1_entrance', 20),
        ('stairs_1_left_corridor', 1),
        ('cafeteria', 1),
    ],

    '1_office104': [('1_corridor', 1), ('1_corridor_104_archive', 1)],
    'archive_first_floor': [('1_corridor', 1), ('1_corridor_104_archive', 1)],

    '1_corridor_104_archive': [
        ('1_corridor', 1),
        ('1_office104', 1),
        ('archive_first_floor', 1),
        ('1_corridor_106_archive', 1),
    ],

    '1_office106': [('1_corridor_106_archive', 1)],
    '1_corridor_106_archive': [
        ('1_office106', 1),
        ('1_corridor_104_archive', 1),
        ('1_corridor_107_121', 1)
    ],

    '1_office107': [('1_corridor_107_121', 1)],
    '1_office121': [('1_corridor_107_121', 1)],
    '1_corridor_107_121': [
        ('1_office107', 1),
        ('1_office121', 1),
        ('1_corridor_106_archive', 1),
        ('1_corridor_120', 1)
    ],

    '1_office120': [('1_corridor_120', 1)],
    '1_corridor_120': [
        ('1_office120', 1),
        ('1_corridor_107_121', 1),
        ('1_corridor_119', 1),
        ('stairs_1_right_corridor', 1),
    ],

    '1_office119': [('1_corridor_119', 1)],

    '2_office203': [('2_corridor', 5)],
    'stairs_1_right_corridor': [
        ('1_corridor_120', 1),
        ('stairs_1_right', 1),

    ],
    'stairs_1_right': [('stairs_2_right', 1)],
    'stairs_1_left': [('stairs_1_left_corridor', 1), ('stairs_2_left', 1)],
    'stairs_1_left_corridor': [
        ('stairs_1_left', 1),
        ('1_corridor', 1),
        ('archive_first_floor', 1),
    ],
    # --- Переход на второй этаж ---
    'stairs_2_left': [
        ('stairs_1_left', 1),  # Узел перехода с первого этажа (лестница) подключается к stairs_2
        ('stairs_2_left_corridor', 1)
    ],
    'stairs_2_left_corridor': [
        ('stairs_2_left', 1),
        ('main_corridor', 1),
    ],

    'stairs_2_right': [
        ('stairs_1_right', 1),  # Узел перехода с первого этажа (лестница) подключается к stairs_2
        ('2_corridor_hall_stair_right', 1)
    ],
    # 'stairs_2_right_corridor': [
    #     ('stairs_2_right', 5),
    #     ('2_corridor_hall_stair_right', 10),
    # ],

    'main_corridor': [
        ('stairs_2_left_corridor', 1),
        ('2_office_225_corridor', 1),
        ('2_office_224_203_corridor', 1),
    ],
    '2_office_225_corridor': [
        ('main_corridor', 1),
        ('2_office_225', 1),
        ('2_office_201', 1),
    ],
    '2_office_225': [
        ('2_office_225_corridor', 1),
    ],
    '2_office_201': [
        ('2_office_225_corridor', 1),
    ],
    '2_office_224': [
        ('2_office_224_203_corridor', 1),
    ],
    '2_office_203': [('2_office_224_203_corridor', 1)],

    '2_office_224_203_corridor': [
        ('2_office_224', 1),
        ('main_corridor', 1),
        ('2_office_203', 1),
        ('2_office_204_corridor', 1),
    ],
    '2_office_204': [('2_office_204_corridor', 1)],
    '2_office_204_corridor': [
        ('2_office_204', 1),
        ('2_office_224_203_corridor', 1),
        ('2_office_205_corridor', 1),
    ],
    '2_office_205': [('2_office_205_corridor', 1)],
    '2_office_206': [('2_office_205_corridor', 1)],
    '2_office_223': [('2_office_205_corridor', 1)],
    '2_office_205_corridor': [
        ('2_office_205', 1),
        ('2_office_223', 1),
        ('2_office_206', 1),
        ('2_office_204_corridor', 1),
        ('2_office_207_208_corridor', 1),
    ],
    '2_office_207': [('2_office_207_208_corridor', 1)],
    '2_office_208': [('2_office_207_208_corridor', 1)],
    '2_office_207_208_corridor': [
        ('2_office_207', 1),
        ('2_office_208', 1),
        ('2_office_204_corridor', 1),
        ('2_corridor_hall_stair_right', 1),
    ],
    '2_hall': [('2_corridor_hall_stair_right', 1)],
    '2_office_222': [('2_corridor_hall_stair_right', 1)],
    '2_corridor_hall_stair_right': [
        ('2_hall', 1),
        ('2_office_207_208_corridor', 1),
        ('stairs_1_right', 1),
        ('2_office_222', 1),
        ('2_corridor_toilet_221_221A', 1),
    ],
    '2_office_221': [('2_corridor_toilet_221_221A', 1)],
    '2_office_221A': [('2_corridor_toilet_221_221A', 1)],
    '2_toilet': [('2_corridor_toilet_221_221A', 1)],
    '2_corridor_toilet_221_221A': [
        ('2_corridor_hall_stair_right', 1),
        ('2_toilet', 1),
        ('2_office_221A', 1),
        ('2_office_221', 1),
        ('2_corridor_220_211', 1),
    ],
    '2_office_220': [('2_corridor_220_211', 1)],
    '2_office_211': [('2_corridor_220_211', 1)],
    '2_corridor_220_211': [
        ('2_corridor_toilet_221_221A', 1),
        ('2_office_211', 1),
        ('2_office_220', 1),
        ('2_corridor_219', 1),
    ],
    '2_office_219': [('2_corridor_219', 1)],
    '2_corridor_219': [
        ('2_corridor_220_211', 1),
        ('2_office_219', 1),
        ('2_corridor_218_212', 1),
    ],
    '2_office_218': [('2_corridor_218_212', 1)],
    '2_office_212': [('2_corridor_218_212', 1)],
    '2_corridor_218_212': [
        ('2_office_212', 1),
        ('2_office_218', 1),
        ('2_corridor_217', 1),
        ('2_corridor_219', 1),
    ],
    '2_office_217': [('2_corridor_217', 1)],
    '2_corridor_217': [
        ('2_office_217', 1),
        ('2_corridor_218_212', 1),
        ('2_corridor_213_216', 1),
    ],
    '2_office_216': [('2_corridor_213_216', 1)],
    '2_office_213': [('2_corridor_213_216', 1)],
    '2_corridor_213_216': [
        ('2_office_216', 1),
        ('2_office_213', 1),
        ('2_corridor_217', 1),
        ('2_corridor_214_215', 1),
    ],
    '2_office_215': [('2_corridor_214_215', 1)],
    '2_office_214': [('2_corridor_214_215', 1)],
    '2_corridor_214_215': [
        ('2_corridor_213_216', 1),
        ('2_office_215', 1),
        ('2_office_214', 1),
        ('2_corridor_214_215', 1),
    ],
    '1_corridor_119': [
        ('1_office119', 1),
        ('1_corridor_120', 1),
        ('1_corridor_118', 1),
    ],
    # --- Продолжение первого этажа ---
    '1_office_118': [('1_corridor_118', 1)],
    '1_corridor_118': [
        ('1_corridor_119', 1),
        ('1_office_118', 1),
        ('1_corridor_117_toilet', 1),
    ],
    '1_office_117': [('1_corridor_117_toilet', 1)],
    'toilet_first_floor': [('1_corridor_117_toilet', 1)],
    '1_corridor_117_toilet': [
        ('1_corridor_118', 1),
        ('toilet_first_floor', 1),
        ('1_office_117', 1),
        ('1_corridor_109_116', 1),
    ],
    '1_office_109': [('1_corridor_109_116', 1)],
    '1_office_116': [('1_corridor_109_116', 1)],
    '1_corridor_109_116': [
        ('1_corridor_117_toilet', 1),
        ('1_office_109', 1),
        ('1_office_116', 1),
        ('1_corridor_110_115', 1),
    ],
    '1_office_110': [('1_corridor_110_115', 1)],
    '1_office_115': [('1_corridor_110_115', 1)],
    '1_corridor_110_115': [
        ('1_office_110', 1),
        ('1_office_115', 1),
        ('1_corridor_109_116', 1),
        ('1_corridor_111_114', 1),
    ],
    '1_office_114': [('1_corridor_111_114', 1)],
    '1_office_111': [('1_corridor_111_114', 1)],
    '1_corridor_111_114': [
        ('1_office_111', 1),
        ('1_office_114', 1),
        ('1_corridor_110_115', 1),
        ('1_corridor_112_113', 1),
    ],
    '1_office_112': [('1_corridor_112_113', 1)],
    '1_office_113': [('1_corridor_112_113', 1)],
    '1_corridor_112_113': [
        ('1_office_113', 1),
        ('1_office_112', 1),
        ('1_corridor_110_115', 1),
    ],
    'cafeteria': [('1_corridor', 1)],

}
graph_5_building = {
    '1_entrance': [('1_corridor_main',  1)],
    '1_corridor_main': [
        ('1_entrance', 1),
        ('1_corridor_cafeteria_wardrobe', 1),
        ('1_corridor_lecture_halls', 1),
        ('1_corridor_stairs_left', 1),
        ('1_corridor_103', 1),

    ],
    '1_wardrobe': [('1_corridor_cafeteria_wardrobe',  1)],
    '1_cafeteria': [('1_corridor_cafeteria_wardrobe',  1)],
    '1_corridor_cafeteria_wardrobe': [
        ('1_cafeteria', 1),
        ('1_wardrobe', 1),
        ('1_corridor_main', 1),
    ],
    '1_corridor_lecture_halls': [
        ('1_corridor_main', 1),
        ('1_corridor_lecture_halls_first', 1),
    ],
    '1_corridor_lecture_halls_first': [
        ('1_corridor_lecture_halls', 1),
        ('1_corridor_assembly_hall', 1),
        ('1_corridor_lecture_halls_right', 1),
    ],
    '1_corridor_assembly_hall': [
        ('1_corridor_lecture_halls_first', 1),
        ('1_assembly_hall', 1),
    ],
    '1_assembly_hall': [('1_corridor_assembly_hall',  1)],
    '1_corridor_lecture_halls_right': [
        ('1_corridor_lecture_halls_first', 1),
        ('1_lecture_halls', 1),
    ],
    '1_lecture_halls': [('1_corridor_lecture_halls_right',  1)],
    '1_corridor_stairs_left': [
        ('1_corridor_main',  1),
        ('1_stairs_left',  1),
    ],
    '1_stairs_left': [('1_corridor_stairs_left',  1)],
    '1_corridor_103': [
        ('1_corridor_main',  1),
        ('1_office_103',  1),
        ('1_corridor_104',  1),
    ],
    '1_office_103': [('1_corridor_103',  1)],
    '1_corridor_104': [
        ('1_corridor_103',  1),
        ('1_office_104',  1),
        ('1_corridor_104A_105',  1),
    ],
    '1_office_104': [('1_corridor_104',  1)],
    '1_corridor_104A_105': [
        ('1_corridor_104',  1),
        ('1_office_104A',  1),
        ('1_office_105',  1),
        ('1_corridor_106',  1),
    ],
    '1_office_104A': [('1_corridor_104A_105',  1)],
    '1_office_105': [('1_corridor_104A_105',  1)],
    '1_corridor_106': [
        ('1_corridor_104A_105',  1),
        ('1_office_106',  1),
        ('1_corridor_108_109',  1),
    ],
    '1_office_106': [('1_corridor_106',  1)],
    '1_corridor_108_109': [
        ('1_corridor_106',  1),
        ('1_office_108',  1),
        ('1_office_109',  1),
        ('1_corridor_110_stairs_first',  1),
    ],
    '1_office_108': [('1_corridor_108_109',  1)],
    '1_office_109': [('1_corridor_108_109',  1)],
    '1_corridor_110_stairs_first': [
        ('1_corridor_108_109',  1),
        ('1_corridor_111',  1),
        ('1_corridor_110_stairs',  1),
    ],
    '1_corridor_110_stairs': [
        ('1_corridor_110_stairs_first',  1),
        ('1_office_110',  1),
        ('1_stairs_right',  1),
    ],
    '1_office_110': [('1_corridor_110_stairs',  1)],
    '1_stairs_right': [('1_corridor_110_stairs',  1)],
    '1_corridor_111': [
        ('1_corridor_110_stairs_first',  1),
        ('1_office_111',  1),
        ('1_corridor_service_toilet',  1),
    ],
    '1_office_111': [('1_corridor_111',  1)],
    '1_corridor_service_toilet': [
        ('1_corridor_111',  1),
        ('1_service_toilet',  1),
        ('1_corridor_toilet_113',  1),
    ],
    '1_service_toilet': [('1_corridor_service_toilet',  1)],
    '1_corridor_toilet_113': [
        ('1_corridor_service_toilet',  1),
        ('1_toilet',  1),
        ('1_office_113',  1),
        ('1_corridor_toilet_112',  1),
    ],
    '1_toilet': [('1_corridor_toilet_113',  1)],
    '1_office_113': [('1_corridor_toilet_113',  1)],
    '1_corridor_toilet_112': [
        ('1_corridor_toilet_113',  1),
        ('1_office_112',  1),
        ('1_corridor_toilet_114_115_116',  1),
    ],
    '1_office_112': [('1_corridor_toilet_112',  1)],
    '1_corridor_toilet_114_115_116': [
        ('1_corridor_toilet_112',  1),
        ('1_office_114',  1),
        ('1_office_115',  1),
        ('1_office_116',  1),
        ('1_corridor_toilet_117_118',  1),
    ],
    '1_office_114': [('1_corridor_toilet_114_115_116',  1)],
    '1_office_115': [('1_corridor_toilet_114_115_116',  1)],
    '1_office_116': [('1_corridor_toilet_114_115_116',  1)],
    '1_corridor_toilet_117_118': [
        ('1_corridor_toilet_112',  1),
        ('1_office_117',  1),
        ('1_office_118',  1),
    ],
    '1_office_117': [('1_corridor_toilet_117_118',  1)],
    '1_office_118': [('1_corridor_toilet_117_118',  1)],

}
target_office = '1_office_118'

coords_floor1_5_building = {
    '1_corridor_toilet_117_118': (1055, 355),
    '1_office_117': (1055, 395),
    '1_office_118': (1055, 321),

    '1_corridor_toilet_114_115_116': (966, 355),
    '1_office_114': (946, 321),
    '1_office_115': (966, 395),
    '1_office_116': (984, 321),

    '1_corridor_toilet_112': (901, 355),
    '1_office_112': (901, 321),

    '1_corridor_toilet_113': (848, 355),
    '1_toilet': (848, 321),
    '1_office_113': (848, 395),

    '1_corridor_service_toilet': (771, 355),
    '1_service_toilet': (771, 321),

    '1_corridor_111': (695, 355),
    '1_office_111': (695, 395),

    '1_corridor_110_stairs_first': (646, 355),
    '1_corridor_110_stairs': (646, 238),
    '1_office_110': (618, 238),
    '1_stairs_right': (671, 238),

    '1_corridor_108_109': (597, 355),
    '1_office_108': (597, 321),
    '1_office_109': (630, 395),

    '1_corridor_106': (564, 355),
    '1_office_106': (564, 321),

    '1_corridor_104A_105': (522, 355),
    '1_office_104A': (522, 321),
    '1_office_105': (522, 395),

    '1_corridor_104': (470, 355),
    '1_office_104': (470, 321),

    '1_corridor_103': (373, 355),
    '1_office_103': (373, 395),

    '1_stairs_left': (300, 292),
    '1_corridor_stairs_left': (250, 292),

    '1_corridor_lecture_halls': (218, 355),
    '1_corridor_lecture_halls_first': (218, 161),
    '1_corridor_assembly_hall': (106, 161),
    '1_corridor_lecture_halls_right': (263, 161),
    '1_assembly_hall': (106, 148),
    '1_lecture_halls': (263, 148),

    '1_corridor_cafeteria_wardrobe': (162, 355),
    '1_cafeteria': (135, 355),
    '1_wardrobe': (162, 392),

    '1_entrance': (250, 445),
    '1_corridor_main': (250, 355),

}

coords_floor1 = {
    'cafeteria': (137, 350),

    '1_corridor_112_113': (1050, 350),
    '1_office_112': (1050, 304),
    '1_office_113': (1050, 380),

    '1_corridor_111_114': (978, 350),
    '1_office_114': (978, 380),
    '1_office_111': (978, 304),

    '1_corridor_110_115': (863, 350),
    '1_office_110': (863, 304),
    '1_office_115': (863, 380),

    '1_corridor_109_116': (823, 350),
    '1_office_109': (823, 304),
    '1_office_116': (823, 380),

    '1_corridor_117_toilet': (735, 350),
    '1_office_117': (735, 380),
    'toilet_first_floor': (735, 304),

    '1_corridor_118': (680, 350),
    '1_office_118': (680, 380),

    'stairs_1_left': (345, 274),
    'stairs_1_right': (623, 214),
    'stairs_1_left_corridor': (240, 274),
    'stairs_1_right_corridor': (605, 214),

    '1_entrance': (240, 500),
    '1_corridor': (240, 350),
    '1_corridor_104_archive': (416, 350),
    '1_corridor_106_archive': (460, 350),
    '1_corridor_107_121': (500, 350),
    '1_corridor_120': (567, 350),
    '1_corridor_119': (630, 350),
    '1_office104': (416, 304),
    '1_office106': (460, 304),
    '1_office107': (520, 304),
    '1_office121': (500, 380),
    '1_office120': (567, 380),
    '1_office119': (630, 380),
    'stairs_1': (400, 300),
    'archive_first_floor': (430, 380),
}
coords_floor2 = {
    '2_corridor_214_215': (966, 280),
    '2_office_215': (966, 312),
    '2_office_214': (966, 240),

    '2_corridor_213_216': (920, 280),
    '2_office_216': (920, 312),
    '2_office_213': (920, 240),

    '2_corridor_217': (881, 280),
    '2_office_217': (881, 312),

    '2_corridor_218_212': (842, 280),
    '2_office_218': (842, 312),
    '2_office_212': (842, 240),

    '2_corridor_219': (797, 280),
    '2_office_219': (797, 312),

    '2_corridor_220_211': (758, 280),
    '2_office_220': (758, 312),
    '2_office_211': (758, 240),

    '2_corridor_toilet_221_221A': (710, 280),
    '2_office_221': (691, 312),
    '2_office_221A': (724, 312),
    '2_toilet': (698, 240),

    '2_office_222': (657, 312),
    '2_office_207_208_corridor': (570, 280),
    '2_office_207': (560, 240),
    '2_office_208': (588, 240),
    '2_hall': (612, 311),
    '2_corridor_hall_stair_right': (612, 280),

    '2_office_205_corridor': (504, 280),
    '2_office_205': (504, 240),
    '2_office_223': (526, 312),
    '2_office_206': (532, 240),

    '2_office_204_corridor': (451, 280),
    '2_office_204': (451, 240),

    '2_office_225_corridor': (304, 330),
    '2_office_225': (338, 330),
    '2_office_201': (267, 370),

    '2_office_224_203_corridor': (396, 280),  # 280 высота коридора
    '2_office_224': (396, 312),
    '2_office_203': (421, 242),

    'stairs_2_left': (364, 163),
    'stairs_2_left_corridor': (304, 163),
    'main_corridor': (304, 280),

    'stairs_2_right': (616, 200),
}

import math
from PIL import Image, ImageDraw

# Изображения этажей
floor_images = {
    "1": r"E:\PycharmProjects\skgu_diplome_api\src\api\search\images\first_floor_6_housingtest.png",
    "2": r"E:\PycharmProjects\skgu_diplome_api\src\api\search\images\second_floor_6_housing.png",
}
floor_images_5_building = {
    "1": r"E:\PycharmProjects\skgu_diplome_api\src\api\search\images\first_floor_5_building.png",
}
floor_coords_5_building = {
    "1": coords_floor1_5_building,
}
floor_coords = {
    "1": coords_floor1,
    "2": coords_floor2,
}

# Константы отладки
DEBUG_SHOW_NODES = True


# Функции поиска пути (BFS/Дейкстра и т.д.)
def bfs_path(graph, start, goal):
    visited = set([start])
    queue = deque([(start, [start])])
    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        for neighbor, _ in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def dijkstra_path(graph, start, goal):
    queue = [(0, start, [start])]
    seen = {start: 0}
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


# Функции для рисования маршрута
def draw_path_with_arrows(image_path, coords_dict, path, out_path, arrow_length=10, arrow_angle=30):
    """
    Рисует маршрут с стрелками, указывающими направление.

    :param image_path: путь к исходному изображению
    :param coords_dict: словарь координат узлов
    :param path: список узлов пути
    :param out_path: путь для сохранения изображения
    :param arrow_length: длина стрелочных "крыльев" (в пикселях)
    :param arrow_angle: угол между линией и стрелочным крылом (в градусах)
    """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Отбираем только те точки, для которых есть координаты на данном этаже
    path_on_this_floor = [p for p in path if p in coords_dict]

    for i in range(len(path_on_this_floor) - 1):
        x1, y1 = coords_dict[path_on_this_floor[i]]
        x2, y2 = coords_dict[path_on_this_floor[i + 1]]

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
        for node, (x, y) in coords_dict.items():
            r = 4  # радиус кружка
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            draw.text((x + 5, y - 5), node, fill='blue')

    img.save(out_path)


def process_route(start_point, target_point):
    """
    Вычисляет путь и генерирует изображения маршрута для каждого этажа.
    Пути к изображениям и координаты берутся из глобальных словарей.
    """
    path = dijkstra_path(graph_5_building, start_point, target_point)
    print("Путь:", path)

    if not path:
        print("Путь не найден.")
        return

    for floor, image_path in floor_images_5_building.items():
        coords = floor_coords_5_building.get(floor)
        if not coords:
            continue

        # Проверяем, есть ли узлы с текущего этажа в построенном пути
        floor_nodes_in_path = [node for node in path if node.startswith(floor + '_') and node in coords]
        if not floor_nodes_in_path:
            continue  # Если нет узлов этажа в пути, переходим к следующему этажу

        # Определяем имя выходного файла для этого этажа
        out_path = f'E:\\PycharmProjects\\skgu_diplome_api\\src\\search\\path_images\\floor_{floor}.png'

        # Рисуем маршрут
        draw_path_with_arrows(image_path, coords, path, out_path)


if __name__ == '__main__':
    start_point = '1_entrance'

    process_route(start_point, target_office)
