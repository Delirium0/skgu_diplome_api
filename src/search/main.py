import heapq
from collections import deque

from PIL import Image, ImageDraw

graph = {
    '1_entrance': [('1_corridor', 20)],
    '1_corridor': [
        ('1_corridor_104_archive', 1),
        ('1_entrance', 20),
        ('stairs_1_left_corridor', 1),
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
    '1_corridor_119': [
        ('1_office119', 1),
        ('1_corridor_120', 1),
    ],

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
}
target_office = '2_office_214'

coords_floor1 = {
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


# 3. Функция поиска пути (BFS/Дейкстра и т.д.)

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


DEBUG_SHOW_NODES = False


def draw_path(image_path, coords_dict, path, out_path):
    """ Рисует маршрут (красная линия) и, при включённом DEBUG, отображает узлы (синие кружки). """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Рисуем сам путь (линии)
    path_on_this_floor = [p for p in path if p in coords_dict]
    for i in range(len(path_on_this_floor) - 1):
        x1, y1 = coords_dict[path_on_this_floor[i]]
        x2, y2 = coords_dict[path_on_this_floor[i + 1]]
        draw.line((x1, y1, x2, y2), fill='red', width=3)

    # Если включен режим отладки, рисуем все узлы с подписями
    if DEBUG_SHOW_NODES:
        for node, (x, y) in coords_dict.items():
            r = 4  # радиус кружка
            draw.ellipse((x - r, y - r, x + r, y + r), fill='blue')
            # Отрисовка подписи узла (можно отключить, если не нужно)
            draw.text((x + 5, y - 5), node, fill='blue')

    img.save(out_path)


if __name__ == '__main__':
    start_point = '1_entrance'
    path = dijkstra_path(graph, start_point, target_office)
    print("Путь:", path)

    draw_path('first_floor_6_housing.png', coords_floor1, path,
              r'E:\PycharmProjects\skgu_diplome_api\src\search\path_images\first.png')
    draw_path('second_floor_6_housing.png', coords_floor2, path,
              r'E:\PycharmProjects\skgu_diplome_api\src\search\path_images\second.png')
