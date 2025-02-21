from typing import List, Dict, Any

from src.api.search.database.models import Location


def format_location_info(location: "Location") -> Dict[str, Any]:
    """
    Форматирует объект Location в словарь нужного формата.
    Асинхронность не требуется, так как функция выполняет только операции в памяти.

    Args:
        location: Объект Location, полученный из базы данных.

    Returns:
        Словарь, содержащий информацию о локации в нужном формате.
    """

    if not location:
        return {}

    bounds_list: List[List[float]] = []
    if location.bounds:
        bounds_list = [[bound.lat, bound.lng] for bound in location.bounds]

    location_info = {
        "lat": location.lat,
        "lng": location.lng,
        "title": location.title,
        "type": location.type,
        "id": location.id,
        "time_start": location.time_start,
        "time_end": location.time_end,
        "main_icon": location.main_icon,
        "address": location.address,
        "bounds": bounds_list,
    }
    return location_info
