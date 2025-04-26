from fastapi import APIRouter, Query, Depends

from src.api.search.schemas import RoutePoints
# Импортируем ВСЕ ТРИ обновленные функции из service.py
from src.api.search.service import get_route, get_location_suggestions, get_route_suggestions

router = APIRouter(prefix='/search', tags=["Search"])


# --- Эндпоинт для подсказок (ИСПРАВЛЕН) ---
# Возвращаем имя параметра 'temp', как ожидает фронтенд
@router.get('/suggest',
            summary="Получить подсказки локаций",
            description="Возвращает список локаций, совпадающих с поисковым запросом `temp`.")
async def get_suggest(
    temp: str = Query(..., description="Поисковый запрос для локации"), # <--- ВОЗВРАЩАЕМ ИМЯ 'temp'
    language: str = Query("ru", description="Язык для названий локаций (ru, en, kz)")
):
    """ Эндпоинт для получения поисковых подсказок. """
    # Вызываем сервисную функцию, передавая значение 'temp' как аргумент 'term'
    result = await get_location_suggestions(term=temp, language=language) # <--- Передаем temp как term
    return result


# --- Эндпоинт для получения маршрута по точным именам узлов ---
@router.get("/route",
            summary="Получить маршрут между двумя точками",
            description="Строит маршрут между точными ID `start` и `target` в `building`.")
async def get_routers(
    route: RoutePoints = Depends(),
    language: str = Query("ru", description="Язык для названий локаций (ru, en, kz)")
):
    """ Эндпоинт для построения маршрута по точным ID. """
    result = await get_route(
        start=route.start,
        target=route.target,
        building=route.building,
        language=language
    )
    return result


# --- Эндпоинт для маршрута по подсказке ---
@router.get("/route_suggestions",
            summary="Получить маршрут по поисковому запросу цели",
            description="Ищет локацию по `target`, берет первый результат и строит маршрут от `start` до него в `building`.")
async def route_suggestions_handler(
    route: RoutePoints = Depends(),
    language: str = Query("ru", description="Язык для названий локаций (ru, en, kz)")
):
    """
    Эндпоинт для построения маршрута, где цель задана поисковым запросом.
    Использует ПЕРВУЮ найденную локацию как цель.
    """
    result = await get_route_suggestions(
        start=route.start,
        target_query=route.target, # target из схемы передается как поисковый запрос
        building=route.building,
        language=language
    )
    return result