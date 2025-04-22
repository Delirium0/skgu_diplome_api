# src/api/faculties/faculty_repo.py
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.singleton_database import DatabaseSingleton
from config import DATABASE_URL
from src.api.faculties.models import Faculty, Department, EducationalProgram
from src.api.faculties.schemas import FacultyCreate, FacultyUpdate


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

    async def get_faculty_by_name(self, name: str) -> Optional[Faculty]:
        """ Вспомогательный метод для поиска факультета по имени (для проверки уникальности). """
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Faculty).where(Faculty.name == name)
            )
            return result.scalars().first()

    async def get_all_faculties(self) -> List[Faculty]:
        async with self.db.session_maker() as session:
            # Сортировка по имени часто удобнее для списков
            result = await session.execute(select(Faculty).order_by(Faculty.name))
            # Не загружаем связи для списка, т.к. FacultyListResponse их не требует
            return result.scalars().all()

    async def create_faculty(self, faculty_data: FacultyCreate) -> Faculty:
        """ Создает новый факультет. Неявно проверяет уникальность имени через get_faculty_by_name в роутере. """
        async with self.db.session_maker() as session:
            faculty = Faculty(**faculty_data.model_dump())  # Pydantic v2
            # faculty = Faculty(**faculty_data.dict()) # Pydantic v1

            session.add(faculty)
            await session.commit()
            await session.refresh(faculty)
            # Загрузим связи, чтобы вернуть полный объект в FacultyResponse
            # т.к. после создания они будут пустыми, но структура ответа их ожидает
            await session.refresh(faculty, attribute_names=['departments', 'educational_programs'])
            return faculty

    async def update_faculty(self, faculty_id: int, faculty_data: FacultyUpdate) -> Optional[Faculty]:
        """ Обновляет факультет. Уникальность имени проверяется в роутере, если имя меняется. """
        async with self.db.session_maker() as session:
            faculty = await session.get(Faculty, faculty_id)
            if not faculty:
                return None  # Не найден

            # Используем model_dump с exclude_unset=True для PATCH-подобного обновления
            update_data = faculty_data.model_dump(exclude_unset=True)  # Pydantic v2
            # update_data = faculty_data.dict(exclude_unset=True) # Pydantic v1

            for key, value in update_data.items():
                setattr(faculty, key, value)

            session.add(faculty)  # Добавляем измененный объект (он уже отслеживается сессией)
            await session.commit()
            await session.refresh(faculty)  # Обновляем объект из БД
            # Подгружаем связи для полного ответа
            await session.refresh(faculty, attribute_names=['departments', 'educational_programs'])
            return faculty

    async def delete_faculty(self, faculty_id: int) -> bool:
        """
        Удаляет факультет по ID. Связанные кафедры и программы удаляются автоматически
        благодаря cascade="all, delete-orphan" в модели Faculty
        и/или ondelete="CASCADE" в ForeignKey моделей Department/EducationalProgram.
        Возвращает True если удаление успешно, False если не найден.
        """
        async with self.db.session_maker() as session:
            faculty = await session.get(Faculty, faculty_id)
            if not faculty:
                return False  # Не найден

            # Не нужно явно удалять связи, SQLAlchemy/БД сделают это
            await session.delete(faculty)
            await session.commit()
            return True


# Инстанс репозитория
faculty_repo = FacultyRepository()
