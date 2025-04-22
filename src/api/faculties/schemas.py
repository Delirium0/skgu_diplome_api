# src/api/faculties/schemas.py
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator


# --- Схемы для связанных сущностей ---
class DepartmentBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True # Pydantic v1


class EducationalProgramBase(BaseModel):
    id: int
    code: str
    name: str
    level: str

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True # Pydantic v1


# --- Основные схемы Факультета ---
class FacultyBase(BaseModel):
    name: str = Field(..., example="Институт информационных технологий", max_length=255)
    description: Optional[str] = Field(None, example="Подробное описание факультета...")
    history: Optional[str] = Field(None, example="История становления факультета...")
    # Можно добавить валидацию для словаря social_links, если нужен конкретный формат
    social_links: Optional[Dict[str, str]] = Field(None, example={"vk": "https://vk.com/faculty",
                                                                  "telegram": "https://t.me/faculty"})
    building: Optional[str] = Field(None, example="Корпус Б", max_length=100)
    address: Optional[str] = Field(None, example="ул. Примерная, д. 10, каб. 205", max_length=255)
    dean_phone: Optional[str] = Field(None, example="+7 (XXX) XXX-XX-XX / Вн. 1234", max_length=100)


class FacultyCreate(FacultyBase):
    name: str = Field(..., example="Институт информационных технологий", max_length=255)


class FacultyUpdate(BaseModel):
    # Все поля опциональны для обновления
    name: Optional[str] = Field(None, example="Новое название Института ИТ", max_length=255)
    description: Optional[str] = Field(None, example="Обновленное описание...")
    history: Optional[str] = Field(None, example="Дополненная история...")
    social_links: Optional[Dict[str, str]] = Field(None, example={"vk": "https://vk.com/new_faculty",
                                                                  "website": "https://new.faculty.site"})
    building: Optional[str] = Field(None, example="Корпус А", max_length=100)
    address: Optional[str] = Field(None, example="ул. Новая, д. 1", max_length=255)
    dean_phone: Optional[str] = Field(None, example="+7 (YYY) YYY-YY-YY", max_length=100)


class FacultyResponse(FacultyBase):
    id: int
    # Связанные данные, используем базовые схемы для них
    departments: List[DepartmentBase] = []
    educational_programs: List[EducationalProgramBase] = []

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True # Pydantic v1


class FacultyListResponse(BaseModel):  # Остается без изменений
    id: int
    name: str

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True # Pydantic v1
