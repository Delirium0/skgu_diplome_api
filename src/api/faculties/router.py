# src/api/faculties/faculty_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

# Убедись, что импорты корректны для твоей структуры проекта
from src.api.faculties.faculty_repo import FacultyRepository, faculty_repo
from src.api.faculties.schemas import FacultyResponse, FacultyListResponse  # Импорт схем

# Можно добавить зависимость от токена, если информация не публичная
# from src.api.auth.service import get_current_user
# from src.api.auth.security import security

router = APIRouter(prefix='/faculties', tags=["Faculties"])


async def get_faculty_repository() -> FacultyRepository:
    return faculty_repo


@router.get("/{faculty_id}", response_model=FacultyResponse)
async def read_faculty(faculty_id: int, repo: FacultyRepository = Depends(get_faculty_repository)):
    """
    Получение детальной информации о факультете по ID,
    включая кафедры и образовательные программы.
    """
    faculty = await repo.get_faculty_by_id(faculty_id)
    if not faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Факультет не найден")
    return faculty


@router.get("/", response_model=List[FacultyListResponse])  # Если нужен список для главной
async def read_faculties(repo: FacultyRepository = Depends(get_faculty_repository)):
    """
    Получение списка всех факультетов (только ID и название).
    """
    faculties = await repo.get_all_faculties()
    return faculties

# Не забудь зарегистрировать этот роутер в твоем основном приложении FastAPI
# Например, в main.py:
# from src.api.faculties import faculty_router
# app.include_router(faculty_router.router)
