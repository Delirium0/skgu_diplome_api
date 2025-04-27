# src/api/admin/schemas.py
from pydantic import BaseModel, Field, EmailStr # EmailStr если логин - email
from typing import Optional, List
from datetime import date # Для поля cmbPeriod

# Схема для отображения информации о пользователе (без паролей)
class UserInfoAdmin(BaseModel):
    id: int
    login: str # Или EmailStr, если используется email
    role: str
    student_id: Optional[int] = None
    semester: Optional[int] = None
    year: Optional[int] = None
    cmbPeriod: Optional[date] = None # Дата
    group_id: Optional[int] = None

    class Config:
        from_attributes = True # Для Pydantic v2+ (или orm_mode = True для v1)

# Схема для создания пользователя админом
class UserCreateAdmin(BaseModel):
    login: str # Или EmailStr
    password: str = Field(..., min_length=4) # Пароль обязателен, мин. длина 4
    role: str # Должна быть одна из: 'user', 'teacher', 'moderator', 'admin'
    student_id: Optional[int] = None
    semester: Optional[int] = None
    year: Optional[int] = None
    cmbPeriod: Optional[date] = None
    group_id: Optional[int] = None

# Схема для обновления пользователя админом (все поля опциональны)
class UserUpdateAdmin(BaseModel):
    login: Optional[str] = None # Или EmailStr
    password: Optional[str] = Field(None, min_length=4) # Пароль не обязателен, но если есть, то мин. 4
    role: Optional[str] = None
    student_id: Optional[int] = None
    semester: Optional[int] = None
    year: Optional[int] = None
    cmbPeriod: Optional[date] = None
    group_id: Optional[int] = None