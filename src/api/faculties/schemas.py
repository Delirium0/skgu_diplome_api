# src/api/faculties/schemas.py (Пример)
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Схемы для связанных сущностей (для полноты) ---
class DepartmentBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True # Для Pydantic v2
        # orm_mode = True # Для Pydantic v1

class EducationalProgramBase(BaseModel):
    id: int
    name: str
    code: Optional[str] = None

    class Config:
        from_attributes = True # Для Pydantic v2
        # orm_mode = True # Для Pydantic v1

# --- Основные схемы Факультета ---
class FacultyBase(BaseModel):
    name: str = Field(..., example="Институт информационных технологий")
    # Добавь другие поля факультета, если они есть

class FacultyCreate(FacultyBase):
    pass # Наследует все поля от FacultyBase

class FacultyUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Новое название Института ИТ")
    # Добавь другие поля, которые можно обновлять, как Optional[...] = None

class FacultyResponse(FacultyBase):
    id: int
    departments: List[DepartmentBase] = [] # Показываем связанные кафедры
    educational_programs: List[EducationalProgramBase] = [] # Показываем связанные программы

    class Config:
        from_attributes = True # Для Pydantic v2
        # orm_mode = True # Для Pydantic v1

class FacultyListResponse(BaseModel): # Для списков (как у тебя уже было)
    id: int
    name: str

    class Config:
        from_attributes = True # Для Pydantic v2
        # orm_mode = True # Для Pydantic v1