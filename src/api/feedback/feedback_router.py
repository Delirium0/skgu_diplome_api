# src/api/feedbacks/feedback_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response

from src.api.auth.models import User
from src.api.auth.service import get_current_user, user_is_admin

from src.api.feedback.feedback_repo import FeedbackRepository, feedback_repo
from src.api.feedback.schemas import (
    FeedbackResponse,
    FeedbackCreate,
    FeedbackUpdate,
)

router = APIRouter(prefix='/feedbacks', tags=["Feedbacks"])


# Зависимость для репозитория
async def get_feedback_repository() -> FeedbackRepository:
    return feedback_repo


@router.post(
    "/",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_feedback(
        feedback_in: FeedbackCreate,
        repo: FeedbackRepository = Depends(get_feedback_repository),
        # Получаем текущего пользователя (студента) из токена
        current_user: User = Depends(get_current_user)
):
    """
    Создание нового отзыва о приложении.
    Доступно для любого аутентифицированного пользователя (студента).
    """
    created_feedback = await repo.create_feedback(
        feedback_data=feedback_in, user_id=current_user.id
    )
    return created_feedback


@router.get(
    "/",
    response_model=List[FeedbackResponse],
    # response_model=List[FeedbackListResponse], # Если используешь отдельную схему
    dependencies=[Depends(user_is_admin)]  # Только админ может видеть все отзывы
)
async def read_all_feedbacks(
        skip: int = 0,
        limit: int = 100,
        repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """
    Получение списка всех отзывов (требуются права администратора).
    """
    feedbacks = await repo.get_all_feedbacks(skip=skip, limit=limit)
    return feedbacks


@router.get(
    "/my",  # Отдельный эндпоинт для получения своих отзывов
    response_model=List[FeedbackResponse]
)
async def read_my_feedbacks(
        skip: int = 0,
        limit: int = 100,
        repo: FeedbackRepository = Depends(get_feedback_repository),
        current_user: User = Depends(get_current_user)
):
    """
    Получение списка отзывов, оставленных текущим пользователем.
    """
    feedbacks = await repo.get_feedbacks_by_user_id(
        user_id=current_user.id, skip=skip, limit=limit
    )
    return feedbacks


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    # Доступ может быть разным: админ может любой, пользователь - свой
    # Здесь для простоты - только админ может смотреть конкретный отзыв по ID
    # Если хочешь разрешить пользователю смотреть свой: добавь Depends(get_current_user)
    # и проверь в коде ниже, что feedback.user_id == current_user.id или user_is_admin
    dependencies=[Depends(user_is_admin)]
)
async def read_feedback(
        feedback_id: int,
        repo: FeedbackRepository = Depends(get_feedback_repository),
        # current_user: User = Depends(get_current_user) # Раскомментируй, если нужна проверка прав
):
    """
    Получение детальной информации об отзыве по ID (требуются права администратора).
    """
    feedback = await repo.get_feedback_by_id(feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")

    # # Пример проверки прав, если не используется dependencies=[Depends(user_is_admin)]
    # is_admin = await user_is_admin(current_user) # Нужна await, если user_is_admin асинхронная
    # if not is_admin and feedback.user_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    return feedback


@router.put(
    "/{feedback_id}",
    response_model=FeedbackResponse
)
async def update_feedback(
        feedback_id: int,
        feedback_in: FeedbackUpdate,
        repo: FeedbackRepository = Depends(get_feedback_repository),
        current_user: User = Depends(get_current_user)  # Пользователь может обновлять только свой отзыв
):
    """
    Обновление существующего отзыва по ID.
    Пользователь может обновить только свой собственный отзыв.
    """
    updated_feedback = await repo.update_feedback(
        feedback_id=feedback_id, feedback_data=feedback_in, user_id=current_user.id
    )
    if not updated_feedback:
        # Это может означать, что отзыв не найден ИЛИ он не принадлежит этому пользователю
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден или у вас нет прав на его изменение"
        )
    return updated_feedback


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(user_is_admin)]
)
async def delete_feedback_by_admin(
        feedback_id: int,
        repo: FeedbackRepository = Depends(get_feedback_repository)
        # current_user больше не нужен здесь
):
    """Удаление отзыва по ID (Администратор)."""
    # Вызываем новый метод репозитория без проверки user_id
    deleted = await repo.delete_feedback_by_admin(feedback_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
