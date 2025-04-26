from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response

from src.api.auth.models import User
from src.api.auth.service import get_current_user, user_is_moderator_or_admin, user_is_admin
from src.api.events.events_repo import EventsRepository, event_repo
from src.api.events.schemas import EventCreate, EventUpdate, EventResponse

router = APIRouter(prefix='/events', tags=["Events"])


async def get_event_repository() -> EventsRepository:
    return event_repo


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
        event_data: EventCreate,
        repo: EventsRepository = Depends(get_event_repository),
        current_user: User = Depends(get_current_user)
):
    """Создание нового события (статус модерации по умолчанию False)."""
    # is_moderate будет False по умолчанию из модели
    return await repo.create_event(event_data, current_user.id)


@router.get("/", response_model=List[EventResponse])
async def read_public_events(repo: EventsRepository = Depends(get_event_repository)):
    """Получение списка всех ОДОБРЕННЫХ событий."""
    return await repo.get_all_events(only_moderated=True)


# GET /events/unmoderated - Получение НЕОДОБРЕННЫХ (для модерации)
@router.get("/unmoderated", response_model=List[EventResponse], dependencies=[Depends(user_is_moderator_or_admin)])
async def read_unmoderated_events(repo: EventsRepository = Depends(get_event_repository)):
    """Получение списка неодобренных событий (Модератор/Админ)."""
    return await repo.get_unmoderated_events()


# GET /events/all - Получение ВСЕХ событий (для админки)
@router.get("/all", response_model=List[EventResponse], dependencies=[Depends(user_is_admin)])
async def read_all_events_admin(repo: EventsRepository = Depends(get_event_repository)):
    """Получение списка ВСЕХ событий (Админ)."""
    return await repo.get_all_events(only_moderated=False)


# PUT /events/{event_id} - Полное обновление события (Админ)
@router.put("/{event_id}", response_model=EventResponse, dependencies=[Depends(user_is_admin)])
async def update_event(
        event_id: int,
        event_data: EventUpdate,  # Теперь включает is_moderate
        repo: EventsRepository = Depends(get_event_repository)
):
    """Обновление события (Админ). Позволяет изменить и статус модерации."""
    updated_event = await repo.update_event(event_id, event_data)
    if not updated_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    return updated_event


# PATCH /events/{event_id}/moderate - Одобрить событие (Модератор/Админ)
@router.patch("/{event_id}/moderate", response_model=EventResponse, dependencies=[Depends(user_is_moderator_or_admin)])
async def moderate_event(
        event_id: int,
        repo: EventsRepository = Depends(get_event_repository)
):
    """Одобрить событие (установить is_moderate = True) (Модератор/Админ)."""
    approved_event = await repo.set_event_moderated(event_id)
    if not approved_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    return approved_event


# DELETE /events/{event_id} - Удаление события (Модератор/Админ)
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(user_is_moderator_or_admin)])
async def delete_event(event_id: int, repo: EventsRepository = Depends(get_event_repository)):
    """Удаление события (Модератор/Админ)."""
    deleted = await repo.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    # Успешный DELETE возвращает 204 No Content, тело не нужно
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# GET /events/{event_id} - Получение одного события по ID (доступно всем)
@router.get("/{event_id}", response_model=EventResponse)
async def read_event(event_id: int, repo: EventsRepository = Depends(get_event_repository)):
    """Получение события по ID."""
    event = await repo.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    # Можно добавить проверку: если event.is_moderate == False, то доступ только админу/модератору?
    # Или оставить доступным всем, если ID известен.
    return event
