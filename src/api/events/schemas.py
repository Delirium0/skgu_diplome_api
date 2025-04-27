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
    event_description: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None


class EventCreate(EventBase):
    pass  # is_moderate по умолчанию False в модели


class EventUpdate(EventBase):
    image_background: Optional[str] = None
    event_creator_name: Optional[str] = None
    event_creator_image: Optional[str] = None
    # event_rating: Optional[float] = None # Рейтинг обычно не обновляется вручную
    event_time: Optional[datetime] = None
    event_name: Optional[str] = None
    event_description: Optional[str] = None # Добавил event_description в схему обновления
    contact_phone: Optional[str] = None  # Добавлено поле contact_phone
    contact_email: Optional[str] = None  # Добавлено поле contact_email
    is_moderate: Optional[bool] = None
    address: Optional[str] = None


class EventResponse(EventBase):
    id: int
    creator_id: int
    is_moderate: bool

    class Config:
        from_attributes = True