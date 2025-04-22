# src/api/faculties/faculty_repo.py
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # Важно для подгрузки связей

from src.database.singleton_database import DatabaseSingleton
from config import DATABASE_URL
from src.api.faculties.models import Faculty, Department, EducationalProgram  # Импортируем все модели
from src.api.faculties.schemas import FacultyCreate  # Если нужна будет функция создания


class FacultyRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def get_faculty_by_id(self, faculty_id: int) -> Optional[Faculty]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Faculty)
                .where(Faculty.id == faculty_id)
                .options(
                    selectinload(Faculty.departments),  # Загружаем кафедры
                    selectinload(Faculty.educational_programs)  # Загружаем программы
                )
            )
            return result.scalars().first()

    async def get_all_faculties(self) -> List[Faculty]:  # Если понадобится список для главной
        async with self.db.session_maker() as session:
            result = await session.execute(select(Faculty).order_by(Faculty.id))
            return result.scalars().all()

    async def create_faculty(self, faculty_data: FacultyCreate):  # Пример создания
        async with self.db.session_maker() as session:
            faculty = Faculty(**faculty_data.model_dump())
            session.add(faculty)
            await session.commit()
            await session.refresh(faculty)
            return faculty


# Инстанс репозитория
faculty_repo = FacultyRepository()
