from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import FileResponse
from typing import List

from src.api.ar.ar_repo import ar_repo
from src.api.ar.schemas import RoomSchema, RoomCreateSchema

router = APIRouter(prefix='/ar', tags=["AR"])

STATIC_AR_URL_BASE = "/static/ar"


@router.get("/config")
async def get_ar_config(building_number: str, floor_number: int) -> FileResponse:
    """
    Возвращает .mind файл для указанного корпуса и этажа.
    """
    try:
        return await ar_repo.get_ar_config(building_number, floor_number)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {e}")


@router.get("/rooms", response_model=List[RoomSchema])
async def get_ar_rooms(building_number: str, floor_number: int):
    """
    Возвращает список комнат для указанного корпуса и этажа.
    """
    rooms = await ar_repo.get_ar_rooms(building_number, floor_number)
    print(rooms)
    try:
        return rooms
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {e}")


@router.post("/rooms", response_model=RoomSchema)
async def add_ar_room(room_data: RoomCreateSchema):
    """
    Добавляет новый кабинет к указанному этажу.
    """
    try:
        return await ar_repo.add_room_to_floor(room_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {e}")
