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
    room_data = RoomCreateSchema(
        room_number="324",
        room_name="Кабинет 324",
        target_index=0,
        description="Описание кабинета 324 (добавлено напрямую через скрипт)",
        building_number="6",
        floor_number=3
    )
    # room_data = RoomCreateSchema(
    #     room_number="322",
    #     room_name="Кабинет 324",
    #     target_index=1,
    #     description="Описание кабинета 324 (добавлено напрямую через скрипт)",
    #     building_number="6",
    #     floor_number=3
    # )
    try:
        new_room = await ar_repo.add_room_to_floor(room_data)
        print("Кабинет успешно добавлен напрямую через репозиторий!")
        print(f"ID кабинета: {new_room.id}")
        print(f"Номер кабинета: {new_room.room_number}")
        print(f"Название кабинета: {new_room.room_name}")
        print(f"Target Index: {new_room.target_index}")
        print(f"Описание: {new_room.description}")
        print(f"Этаж ID: {new_room.floor_id}")

    except Exception as e:
        print(f"Ошибка при добавлении кабинета: {e}")

if __name__ == "__main__":
    asyncio.run(add_room_directly())