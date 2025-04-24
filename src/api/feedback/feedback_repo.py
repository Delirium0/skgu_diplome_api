# src/api/feedbacks/feedback_repo.py
from typing import List, Optional

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.singleton_database import DatabaseSingleton
from config import DATABASE_URL # Или твой способ получения URL БД
from src.api.feedback.models import Feedback
from src.api.feedback.schemas import FeedbackCreate, FeedbackUpdate


class FeedbackRepository:
    def __init__(self):
        # Используем твой существующий DatabaseSingleton
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def create_feedback(self, feedback_data: FeedbackCreate, user_id: int) -> Feedback:
        """Создает новый отзыв в БД."""
        async with self.db.session_maker() as session:
            # Создаем словарь данных, включая user_id
            db_feedback_data = feedback_data.model_dump() # Pydantic v2
            # db_feedback_data = feedback_data.dict() # Pydantic v1
            db_feedback_data['user_id'] = user_id

            feedback = Feedback(**db_feedback_data)
            session.add(feedback)
            await session.commit()
            await session.refresh(feedback)
            return feedback

    async def get_feedback_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Получает отзыв по ID."""
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Feedback).where(Feedback.id == feedback_id)
            )
            return result.scalars().first()

    async def get_all_feedbacks(self, skip: int = 0, limit: int = 100) -> List[Feedback]:
        """Получает список всех отзывов с пагинацией."""
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Feedback)
                .order_by(Feedback.created_at.desc()) # Сортируем по дате (сначала новые)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()

    async def get_feedbacks_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Feedback]:
        """Получает список отзывов конкретного пользователя."""
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Feedback)
                .where(Feedback.user_id == user_id)
                .order_by(Feedback.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()

    async def update_feedback(
        self, feedback_id: int, feedback_data: FeedbackUpdate, user_id: int
    ) -> Optional[Feedback]:
        """
        Обновляет отзыв.
        Важно: Проверяет, что обновляемый отзыв принадлежит user_id.
        """
        async with self.db.session_maker() as session:
            # Сначала найдем отзыв, убедившись, что он принадлежит пользователю
            feedback = await session.execute(
                select(Feedback).where(Feedback.id == feedback_id, Feedback.user_id == user_id)
            )
            feedback = feedback.scalars().first()

            if not feedback:
                return None # Не найден или не принадлежит пользователю

            # Получаем данные для обновления, исключая неустановленные поля (для PATCH-подобного поведения)
            update_data = feedback_data.model_dump(exclude_unset=True) # Pydantic v2
            # update_data = feedback_data.dict(exclude_unset=True) # Pydantic v1

            if not update_data: # Если нечего обновлять
                return feedback # Возвращаем как есть

            # Обновляем поля
            for key, value in update_data.items():
                setattr(feedback, key, value)

            session.add(feedback) # Добавляем измененный объект
            await session.commit()
            await session.refresh(feedback)
            return feedback

    async def delete_feedback(self, feedback_id: int, user_id: int) -> bool:
        """
        Удаляет отзыв.
        Важно: Проверяет, что удаляемый отзыв принадлежит user_id.
        Возвращает True если удаление успешно, False если не найден или не принадлежит пользователю.
        """
        async with self.db.session_maker() as session:
            # Проверяем существование и принадлежность отзыва перед удалением
            feedback = await session.execute(
                select(Feedback).where(Feedback.id == feedback_id, Feedback.user_id == user_id)
            )
            feedback = feedback.scalars().first()

            if not feedback:
                return False # Не найден или не принадлежит пользователю

            await session.delete(feedback)
            await session.commit()
            return True

# Инстанс репозитория
feedback_repo = FeedbackRepository()