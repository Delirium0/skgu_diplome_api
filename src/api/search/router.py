from fastapi import APIRouter, Query, Depends

from src.api.search.schemas import RoutePoints
from src.api.search.service import get_route, get_temps, get_route_suggestions

router = APIRouter(prefix='/search', tags=["Search"])


@router.get('/suggest')
async def get_suggest(temp: str = Query(..., description="Search term")):
    result = await get_temps(temp)
    return result


@router.get("/route")
async def get_routers(route: RoutePoints = Depends()):
    result = await get_route(route.start, route.target, route.building)
    return result


@router.get("/route_suggestions")
async def route_suggestions(route: RoutePoints = Depends()):
    result = await get_route_suggestions(route.start, route.target, route.building)
    return result
