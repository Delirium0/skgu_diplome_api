# src/api/feedbacks/models.py
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Text, ForeignKey, DateTime, func, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.auth.models import User
from src.database.database import Base


class Feedback(Base):
    """
    Модель отзыва о приложении, оставленного студентом.
    """
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, comment="Оценка от 1 до 5")
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Текстовый комментарий отзыва")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Время создания отзыва"
    )

    # Связь с пользователем (студентом), который оставил отзыв
    user_id: Mapped[int] = mapped_column(
        Integer,
        # Укажи правильный путь к primary key твоей таблицы users
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="feedbacks")

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, user_id={self.user_id}, rating={self.rating})>"
