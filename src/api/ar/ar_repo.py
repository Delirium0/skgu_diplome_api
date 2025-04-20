from typing import Optional, List
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import selectinload

from config import DATABASE_URL
from src.api.ar.schemas import RoomCreateSchema
from src.api.search.database.models import Floor, Room
from src.database.singleton_database import DatabaseSingleton


class ARRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def get_ar_config(self, building_number: str, floor_number: int) -> FileResponse:
        """
        Получает конфигурацию AR, включая содержимое .mind файла, для указанного корпуса и этажа.
        """
        async with self.db.session_maker() as session:
            floor = await session.execute(
                select(Floor)
                .where(Floor.building_number == building_number)
                .where(Floor.floor_number == floor_number)
            )
            floor = floor.scalar_one_or_none()

            if not floor:
                raise HTTPException(status_code=404, detail="Этаж не найден")

            if not floor.mind_file_path:
                raise HTTPException(status_code=404, detail="Для этого этажа не настроен AR")

            file_path = floor.mind_file_path

            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_dir = os.path.join(current_dir, '..', '..', '..', 'static', 'ar', file_path)

            print(f"Полный путь к файлу: {file_dir}")

            if not os.path.exists(file_dir):
                raise HTTPException(status_code=500, detail=f"Файл не найден по пути: {file_dir}")

            return FileResponse(file_dir, media_type='application/octet-stream', filename="target.mind")

    async def get_ar_rooms(self, building_number: str, floor_number: int) -> List[Room]:
        """
        Получает список комнат для указанного корпуса и этажа.
        """
        async with self.db.session_maker() as session:
            floor = await session.execute(
                select(Floor)
                .where(Floor.building_number == building_number)
                .where(Floor.floor_number == floor_number)
                .options(selectinload(Floor.rooms))
            )
            floor = floor.scalar_one_or_none()

            if not floor:
                raise HTTPException(status_code=404, detail="Этаж не найден")

            return floor.rooms

    async def add_room_to_floor(self, room_data: RoomCreateSchema) -> Room:
        """
        Добавляет новый кабинет к указанному этажу.
        """
        async with self.db.session_maker() as session:
            floor = await session.execute(
                select(Floor)
                .where(Floor.building_number == room_data.building_number)
                .where(Floor.floor_number == room_data.floor_number)
            )
            floor = floor.scalar_one_or_none()

            if not floor:
                raise HTTPException(status_code=404, detail="Этаж не найден")

            new_room = Room(
                room_number=room_data.room_number,
                room_name=room_data.room_name,
                target_index=room_data.target_index,
                description=room_data.description,
                floor_id=floor.id,  # Связываем комнату с этажом через floor_id
                floor=floor  # и явно устанавливаем связь для ORM
            )
            session.add(new_room)
            await session.commit()
            await session.refresh(new_room)  # Обновляем объект, чтобы получить сгенерированный ID
            return new_room


ar_repo = ARRepository()
