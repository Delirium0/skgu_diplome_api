# src/api/ar/ar_router.py

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from src.api.ar.ar_repo import ar_repo

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
