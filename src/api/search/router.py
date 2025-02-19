from fastapi import routing, APIRouter, Query, Depends

from src.api.search.Service import get_temps, get_route
from src.api.search.schemas import RoutePoints

router = APIRouter(prefix='/search')


@router.get('/suggest')
async def get_suggest(temp: str = Query(..., description="Search term")):
    result = await get_temps(temp)
    return result


@router.get("/route")
async def get_routers(route: RoutePoints = Depends()):
    result = await get_route(route.start, route.target, route.building)
    return result
