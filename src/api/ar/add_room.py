import asyncio

from src.api.ar.ar_repo import ARRepository
from src.api.ar.schemas import RoomCreateSchema


async def add_room_directly():
    """
    Добавляет кабинет напрямую через репозиторий.
    """
    ar_repo = ARRepository()

    # Данные для нового кабинета (соответствуют RoomCreateSchema)
    # room_data = RoomCreateSchema(
    #     room_number="209",
    #     room_name="Кабинет 209",
    #     target_index=0,
    #     description="Описание кабинета 209 (добавлено напрямую через скрипт)",
    #     building_number="6",
    #     floor_number=1
    # )
    # room_data = RoomCreateSchema(
    #     room_number="324",
    #     room_name="Кабинет 324",
    #     target_index=0,
    #     description="Описание кабинета 324 (добавлено напрямую через скрипт)",
    #     building_number="6",
    #     floor_number=3
    # )
    # room_data = RoomCreateSchema(
    #     room_number="322",
    #     room_name="Кабинет 324",
    #     target_index=1,
    #     description="Описание кабинета 324 (добавлено напрямую через скрипт)",
    #     building_number="6",
    #     floor_number=3
    # )
    # Кабинет 203
    # Assuming 'ar_repo' is an instance of your repository class
    # and this code is running inside an async function

    # Кабинет 203
    room_data_203 = RoomCreateSchema(
        room_number="203",
        room_name="Кабинет 203",
        target_index=0,
        description="Описание кабинета 203 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_203 = await ar_repo.add_room_to_floor(room_data_203)

    # Кабинет 204
    room_data_204 = RoomCreateSchema(
        room_number="204",
        room_name="Кабинет 204",
        target_index=1,
        description="Описание кабинета 204 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_204 = await ar_repo.add_room_to_floor(room_data_204)

    # Кабинет 205
    room_data_205 = RoomCreateSchema(
        room_number="205",
        room_name="Кабинет 205",
        target_index=2,
        description="Описание кабинета 205 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_205 = await ar_repo.add_room_to_floor(room_data_205)

    # Кабинет 206
    room_data_206 = RoomCreateSchema(
        room_number="206",
        room_name="Кабинет 206",
        target_index=3,
        description="Описание кабинета 206 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_206 = await ar_repo.add_room_to_floor(room_data_206)

    # Кабинет 207
    room_data_207 = RoomCreateSchema(
        room_number="207",
        room_name="Кабинет 207",
        target_index=4,
        description="Описание кабинета 207 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_207 = await ar_repo.add_room_to_floor(room_data_207)

    # Кабинет 208
    room_data_208 = RoomCreateSchema(
        room_number="208",
        room_name="Кабинет 208",
        target_index=5,
        description="Описание кабинета 208 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_208 = await ar_repo.add_room_to_floor(room_data_208)

    # Кабинет 209
    room_data_209 = RoomCreateSchema(
        room_number="209",
        room_name="Кабинет 209",
        target_index=6,
        description="Описание кабинета 209 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_209 = await ar_repo.add_room_to_floor(room_data_209)

    # Кабинет 210
    room_data_210 = RoomCreateSchema(
        room_number="210",
        room_name="Кабинет 210",
        target_index=7,
        description="Описание кабинета 210 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_210 = await ar_repo.add_room_to_floor(room_data_210)

    # Кабинет 211
    room_data_211 = RoomCreateSchema(
        room_number="211",
        room_name="Кабинет 211",
        target_index=8,
        description="Описание кабинета 211 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_211 = await ar_repo.add_room_to_floor(room_data_211)

    # Кабинет 213
    room_data_213 = RoomCreateSchema(
        room_number="213",
        room_name="Кабинет 213",
        target_index=9,
        description="Описание кабинета 213 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_213 = await ar_repo.add_room_to_floor(room_data_213)

    # Кабинет 215
    room_data_215 = RoomCreateSchema(
        room_number="215",
        room_name="Кабинет 215",
        target_index=10,
        description="Описание кабинета 215 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_215 = await ar_repo.add_room_to_floor(room_data_215)

    # Кабинет 218
    room_data_218 = RoomCreateSchema(
        room_number="218",
        room_name="Кабинет 218",
        target_index=11,
        description="Описание кабинета 218 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_218 = await ar_repo.add_room_to_floor(room_data_218)

    # Кабинет 219
    room_data_219 = RoomCreateSchema(
        room_number="219",
        room_name="Кабинет 219",
        target_index=12,
        description="Описание кабинета 219 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_219 = await ar_repo.add_room_to_floor(room_data_219)

    # Кабинет 221
    room_data_221 = RoomCreateSchema(
        room_number="221",
        room_name="Кабинет 221",
        target_index=13,
        description="Описание кабинета 221 (добавлено напрямую через скрипт)",
        building_number="5",
        floor_number=2
    )
    new_room_221 = await ar_repo.add_room_to_floor(room_data_221)

    # --- Или в цикле, если собрать данные в список ---
    # all_room_data = [
    #     room_data_203, room_data_204, room_data_205, room_data_206, room_data_207,
    #     room_data_208, room_data_209, room_data_210, room_data_211, room_data_213,
    #     room_data_215, room_data_218, room_data_219, room_data_221
    # ]
    #
    # added_rooms = []
    # for room_data in all_room_data:
    #     new_room = await ar_repo.add_room_to_floor(room_data)
    #     added_rooms.append(new_room)
    #     print(f"Добавлен кабинет: {new_room.room_number}") # Пример вывода

    # --- Возможно, вам понадобится собрать их в список ---
    # all_room_data = [
    #     room_data_203, room_data_204, room_data_205, room_data_206, room_data_207,
    #     room_data_208, room_data_209, room_data_210, room_data_211, room_data_213,
    #     room_data_215, room_data_218, room_data_219, room_data_221
    # ]
    try:
        # new_room = await ar_repo.add_room_to_floor(room_data)
        # print("Кабинет успешно добавлен напрямую через репозиторий!")
        # print(f"ID кабинета: {new_room.id}")
        # print(f"Номер кабинета: {new_room.room_number}")
        # print(f"Название кабинета: {new_room.room_name}")
        # print(f"Target Index: {new_room.target_index}")
        # print(f"Описание: {new_room.description}")
        # print(f"Этаж ID: {new_room.floor_id}")
        pass

    except Exception as e:
        print(f"Ошибка при добавлении кабинета: {e}")

if __name__ == "__main__":
    asyncio.run(add_room_directly())