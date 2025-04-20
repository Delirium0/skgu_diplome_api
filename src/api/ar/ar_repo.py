# src/api/ar/ar_repository.py
from typing import Optional
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Response
from fastapi.responses import FileResponse

from config import DATABASE_URL
from src.api.search.database.models import Floor
from src.database.singleton_database import DatabaseSingleton


class ARRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def get_ar_config(self, building_number: str, floor_number: int) -> FileResponse: # Изменяем тип возвращаемого значения
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

            file_path = floor.mind_file_path # Получаем относительный путь из базы данных (например, 'building_6/floor_1.mind')

            # Построение абсолютного пути к файлу static/ar
            current_dir = os.path.dirname(os.path.abspath(__file__)) # Путь к директории ar_repository.py (src/api/ar)
            file_dir = os.path.join(current_dir, '..', '..', '..', 'static', 'ar', file_path) # Исправлено "statis" на "static" и убрал лишний уровень ..

            print(f"Полный путь к файлу: {file_dir}") # Печатаем полный путь для отладки

            if not os.path.exists(file_dir): # Проверяем существование файла по полному пути file_dir
                raise HTTPException(status_code=500, detail=f"Файл не найден по пути: {file_dir}") # Используем file_dir в сообщении об ошибке

            return FileResponse(file_dir, media_type='application/octet-stream', filename="target.mind") # Отправляем файл как FileResponse, используя file_dir

ar_repo = ARRepository()