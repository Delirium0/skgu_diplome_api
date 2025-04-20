from pydantic import BaseModel


class RoomSchema(BaseModel):
    id: int
    room_number: str
    room_name: str
    target_index: int
    description: str | None

    class Config:
        orm_mode = True