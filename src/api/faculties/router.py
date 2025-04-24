# src/api/faculties/faculty_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request  # Добавили Request

# --- ВАШИ ИМПОРТЫ АУТЕНТИФИКАЦИИ ---
# Убедись, что пути импорта корректны для твоего проекта
from src.api.auth.security import security  # Используется в get_current_user
from src.api.auth.user_repo import user_repository  # Используется в get_current_user
# --- ИМПОРТЫ ДЛЯ ФАКУЛЬТЕТОВ ---
from src.api.faculties.faculty_repo import FacultyRepository, faculty_repo
from src.api.faculties.schemas import (
    FacultyResponse,
    FacultyListResponse,
    FacultyCreate,
    FacultyUpdate
)
from src.api.auth.service import get_current_user, user_is_admin

# Единый роутер для всех операций с факультетами
router = APIRouter(prefix='/faculties', tags=["Faculties"])


async def get_faculty_repository() -> FacultyRepository:
    """Зависимость для получения экземпляра репозитория."""
    return faculty_repo


@router.post(
    "/",
    response_model=FacultyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(user_is_admin)]
)
async def create_faculty(
        faculty_in: FacultyCreate,
        repo: FacultyRepository = Depends(get_faculty_repository)
):
    """
    Создание нового факультета (требуются права администратора).
    """
    # Проверка на уникальность имени перед созданием
    existing_faculty = await repo.get_faculty_by_name(faculty_in.name)
    if existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Факультет с именем '{faculty_in.name}' уже существует."
        )
    created_faculty = await repo.create_faculty(faculty_data=faculty_in)
    return created_faculty


@router.get("/", response_model=List[FacultyListResponse])
async def read_faculties(
        repo: FacultyRepository = Depends(get_faculty_repository)
):
    """
    Получение списка всех факультетов (ID и название). Доступно всем.
    """
    faculties = await repo.get_all_faculties()
    return faculties


@router.get("/{faculty_id}", response_model=FacultyResponse)
async def read_faculty(
        faculty_id: int,
        repo: FacultyRepository = Depends(get_faculty_repository)
):
    """
    Получение детальной информации о факультете по ID,
    включая кафедры и образовательные программы. Доступно всем.
    """
    faculty = await repo.get_faculty_by_id(faculty_id)
    if not faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Факультет не найден")
    return faculty


@router.put(
    "/{faculty_id}",
    response_model=FacultyResponse,
    dependencies=[Depends(user_is_admin)]
)
async def update_faculty(
        faculty_id: int,
        faculty_in: FacultyUpdate,
        repo: FacultyRepository = Depends(get_faculty_repository)
):
    """
    Обновление существующего факультета по ID (требуются права администратора).
    """
    faculty_to_update = await repo.get_faculty_by_id(faculty_id)
    if not faculty_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Факультет не найден")

    if faculty_in.name is not None and faculty_in.name != faculty_to_update.name:
        existing_faculty_with_new_name = await repo.get_faculty_by_name(faculty_in.name)
        if existing_faculty_with_new_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Факультет с именем '{faculty_in.name}' уже существует."
            )

    updated_faculty = await repo.update_faculty(faculty_id=faculty_id, faculty_data=faculty_in)
    return updated_faculty


@router.delete(
    "/{faculty_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(user_is_admin)]
)
async def delete_faculty(
        faculty_id: int,
        repo: FacultyRepository = Depends(get_faculty_repository)
):
    """
    Удаление факультета по ID (требуются права администратора).
    """
    deleted = await repo.delete_faculty(faculty_id=faculty_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Факультет не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


