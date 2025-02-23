from fastapi import APIRouter, Query, Depends

from src.api.search.schemas import RoutePoints
from src.api.search.service import get_route, get_temps

router = APIRouter(prefix='/search')


@router.get('/suggest')
async def get_suggest(temp: str = Query(..., description="Search term")):
    result = await get_temps(temp)
    return result


@router.get("/route")
async def get_routers(route: RoutePoints = Depends()):
    result = await get_route(route.start, route.target, route.building)
    return result
