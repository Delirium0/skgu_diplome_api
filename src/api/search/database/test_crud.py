get_location_names = {
    '1_entrance': 'Вход',
    '1_office104': 'Кабинет 104',
    '1_office106': 'Кабинет 106',
    '1_office107': 'Кабинет 107',
    '1_office121': 'Кабинет 121',
    '1_office120': 'Кабинет 120',
    '1_office119': 'Кабинет 119',
    'archive_first_floor': 'Архив',
    'stairs_1_left': 'Лестница (левая)',
    'stairs_1_right': 'Лестница (правая)',
    '2_office_201': 'Кабинет 201',
    '2_office_203': 'Кабинет 203',
    '2_office_204': 'Кабинет 204',
    '2_office_205': 'Кабинет 205',
    '2_office_206': 'Кабинет 206',
    '2_office_207': 'Кабинет 207',
    '2_office_208': 'Кабинет 208',
    '2_office_211': 'Кабинет 211',
    '2_office_212': 'Кабинет 212',
    '2_office_213': 'Кабинет 213',
    '2_office_214': 'Кабинет 214',
    '2_office_215': 'Кабинет 215',
    '2_office_216': 'Кабинет 216',
    '2_office_217': 'Кабинет 217',
    '2_office_218': 'Кабинет 218',
    '2_office_219': 'Кабинет 219',
    '2_office_220': 'Кабинет 220',
    '2_office_221': 'Кабинет 221',
    '2_office_221A': 'Кабинет 221A',
    '2_office_222': 'Кабинет 222',
    '2_office_223': 'Кабинет 223',
    '2_office_225': 'Кабинет 225',
    '2_office_224': 'Кабинет 224',
    '1_office_108': 'Кабинет 108',
    '2_hall': 'Холл',
    '2_toilet': 'Туалет',
    'library': 'library',
    'stairs_2_left': 'Лестница (левая, 2 этаж)',
    'stairs_2_right': 'Лестница (правая, 2 этаж)',
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

get_graph = {
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
