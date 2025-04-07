from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventBase(BaseModel):
    image_background: str
    event_creator_name: str
    event_creator_image: Optional[str] = None
    event_rating: Optional[float] = None
    event_time: datetime
    event_name: str
    event_description: Optional[str] = None # Добавил event_description в базовую схему, так как он есть в модели
    contact_phone: Optional[str] = None  # Добавлено поле contact_phone
    contact_email: Optional[str] = None  # Добавлено поле contact_email


class EventCreate(EventBase):
    event_description: Optional[str] = None # Добавил event_description в схему создания
    contact_phone: Optional[str] = None  # Добавлено поле contact_phone
    contact_email: Optional[str] = None  # Добавлено поле contact_email
    pass


class EventUpdate(EventBase):
    image_background: Optional[str] = None
    event_creator_name: Optional[str] = None
    event_creator_image: Optional[str] = None
    event_rating: Optional[float] = None
    event_time: Optional[datetime] = None
    event_name: Optional[str] = None
    event_description: Optional[str] = None # Добавил event_description в схему обновления
    contact_phone: Optional[str] = None  # Добавлено поле contact_phone
    contact_email: Optional[str] = None  # Добавлено поле contact_email


class EventResponse(EventBase):
    id: int
    event_description: Optional[str] = None # Добавил event_description в схему ответа

    class Config:
        from_attributes = True