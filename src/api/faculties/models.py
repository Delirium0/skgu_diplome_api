# src/api/faculties/models.py
from typing import List, Optional, Dict
from sqlalchemy import String, Integer, Identity, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Пока оставим простыми полями, можно будет развить в отдельные таблицы
    social_links: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON,
                                                                   nullable=True)  # Пример: {"vk": "url", "instagram": "url"}
    building: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dean_phone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Внутренний + основной

    # Связи с кафедрами и программами
    departments: Mapped[List["Department"]] = relationship(back_populates="faculty", cascade="all, delete-orphan")
    educational_programs: Mapped[List["EducationalProgram"]] = relationship(back_populates="faculty",
                                                                            cascade="all, delete-orphan")

    # Добавь __repr__ для удобства отладки
    def __repr__(self) -> str:
        return f"<Faculty(id={self.id}, name='{self.name}')>"


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Дополнительные поля для кафедры, если нужны (например, ссылка на страницу кафедры)
    # link: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), nullable=False)
    faculty: Mapped["Faculty"] = relationship(back_populates="departments")

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name='{self.name}', faculty_id={self.faculty_id})>"


class EducationalProgram(Base):
    __tablename__ = "educational_programs"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # Например, 6B10101
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Например, Общая медицина
    level: Mapped[str] = mapped_column(String(50), nullable=False)  # Бакалавриат, Магистратура и т.д.
    # Дополнительные поля, если нужны (например, ссылка на описание программы)
    # link: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), nullable=False)
    faculty: Mapped["Faculty"] = relationship(back_populates="educational_programs")

    def __repr__(self) -> str:
        return f"<EducationalProgram(id={self.id}, code='{self.code}', name='{self.name}', faculty_id={self.faculty_id})>"

