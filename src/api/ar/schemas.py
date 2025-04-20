from pydantic import BaseModel, Field


class RoomSchema(BaseModel):
    id: int
    room_number: str
    room_name: str
    target_index: int
    description: str | None

    class Config:
        orm_mode = True


class RoomCreateSchema(BaseModel):
    room_number: str = Field(..., description="Номер кабинета")
    room_name: str = Field(..., description="Название кабинета")
    target_index: int = Field(..., description="Индекс цели в AR (0, 1, 2...)")
    description: str | None = Field(None, description="Описание кабинета")
    building_number: str = Field(..., description="Номер корпуса")
    floor_number: int = Field(..., description="Номер этажа")