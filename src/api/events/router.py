from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth.security import security
from src.api.auth.service import get_current_user
from src.api.events.events_repo import EventsRepository, event_repo
from src.api.events.schemas import EventCreate, EventUpdate, EventResponse

router = APIRouter(prefix='/events', tags=["Events"])


async def get_event_repository() -> EventsRepository:
    return event_repo


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(security.access_token_required)])
async def create_event(event_data: EventCreate, repo: EventsRepository = Depends(get_event_repository),
                       current_user=Depends(get_current_user)):
    """Создание нового события."""
    return await repo.create_event(event_data, current_user.id)


@router.get("/{event_id}", response_model=EventResponse)
async def read_event(event_id: int, repo: EventsRepository = Depends(get_event_repository)):
    """Получение события по ID."""
    event = await repo.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    return event


@router.get("/", response_model=List[EventResponse])
async def read_events(repo: EventsRepository = Depends(get_event_repository)):
    """Получение списка всех событий."""
    return await repo.get_all_events()


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, event_data: EventUpdate, repo: EventsRepository = Depends(get_event_repository)):
    """Обновление события."""
    updated_event = await repo.update_event(event_id, event_data)
    if not updated_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    return updated_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, repo: EventsRepository = Depends(get_event_repository)):
    """Удаление события."""
    deleted = await repo.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    return {"detail": "Событие успешно удалено"}
