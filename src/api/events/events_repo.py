from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, joinedload

from config import DATABASE_URL
from src.database.singleton_database import DatabaseSingleton
from src.api.events.models import Event
from src.api.events.schemas import EventCreate, EventUpdate


class EventsRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def create_event(self, event_data: EventCreate, user_id: int) -> Event:
        """Создает новое событие в базе данных, автоматически устанавливая creator_id."""
        async with self.db.session_maker() as session:
            event = Event(**event_data.model_dump())
            event.creator_id = user_id
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event

    async def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Получает событие по ID, загружая информацию о создателе."""
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Event)
                .where(Event.id == event_id)
                .options(joinedload(Event.creator))  # Eager loading создателя
            )
            return result.scalar_one_or_none()

    async def get_all_events(self, only_moderated: bool = False) -> List[Event]:
        """
        Получает все события. Если only_moderated=True, возвращает только одобренные.
        Загружает информацию о создателях.
        """
        async with self.db.session_maker() as session:
            stmt = select(Event).options(joinedload(Event.creator)).order_by(
                Event.id.desc())  # Сортировка по ID или дате
            if only_moderated:
                stmt = stmt.where(Event.is_moderate == True)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_unmoderated_events(self) -> List[Event]:
        """Получает все неодобренные события."""
        async with self.db.session_maker() as session:
            stmt = select(Event).where(Event.is_moderate == False).options(joinedload(Event.creator)).order_by(
                Event.id.asc())  # Сначала старые
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_event(self, event_id: int, event_data: EventUpdate) -> Optional[Event]:
        """Обновляет существующее событие."""
        async with self.db.session_maker() as session:
            event = await session.get(Event, event_id)
            if event:
                update_values = event_data.model_dump(exclude_unset=True)
                if not update_values:  # Если нечего обновлять
                    return event  # Возвращаем как есть
                for key, value in update_values.items():
                    setattr(event, key, value)
                await session.commit()
                await session.refresh(event, attribute_names=['creator'])
                return event
            return None

    async def set_event_moderated(self, event_id: int) -> Optional[Event]:
        """Устанавливает is_moderate = True для события."""
        async with self.db.session_maker() as session:
            event = await session.get(Event, event_id)
            if event:
                if not event.is_moderate:  # Обновляем только если еще не одобрено
                    event.is_moderate = True
                    await session.commit()
                    await session.refresh(event, attribute_names=['creator'])
                return event
            return None

    async def delete_event(self, event_id: int) -> bool:
        """Удаляет событие по ID."""
        async with self.db.session_maker() as session:
            event = await session.get(Event, event_id)
            if event:
                await session.delete(event)
                await session.commit()
                return True
            return False


event_repo = EventsRepository()
