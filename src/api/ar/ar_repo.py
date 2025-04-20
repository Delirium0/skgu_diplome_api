from typing import Optional, List
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import selectinload

from config import DATABASE_URL
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
                .options(selectinload(Floor.rooms)) # Eager load rooms чтобы rooms были загружены сразу
            )
            floor = floor.scalar_one_or_none()

            if not floor:
                raise HTTPException(status_code=404, detail="Этаж не найден")

            return floor.rooms

ar_repo = ARRepository()