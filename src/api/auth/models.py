from typing import Optional

from sqlalchemy import Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from typing import List, TYPE_CHECKING

from src.database.database import Base

if TYPE_CHECKING:
    from src.api.feedback.models import Feedback


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    password_no_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # admin\user\teacher\moderator

    student_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 67426
    semester: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 2024
    cmbPeriod: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)  # 2025-04-07
    group_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 6207
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="user",
        cascade="all, delete-orphan"
    )
