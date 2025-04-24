import asyncio
import base64
import heapq
import io
import math
import os
from typing import List, Dict, Any, Optional

from PIL import Image, ImageDraw
from fastapi import HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.orm import joinedload

from config import DATABASE_URL
from src.api.search.database.models import Floor, Node, Edge, Location, Bounds
from src.api.locations.service import image_to_base64
from src.database.singleton_database import DatabaseSingleton

DEBUG_SHOW_NODES = False


class MapPointsRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def add_location(self, lat: float, lng: float, title: str, type_: str, address: str,
                           time_start: str | None, time_end: str | None, main_icon: str | None,
                           bounds: list[tuple[float, float]], building_type: str | None,
                           building_type_name_ru: str | None):
        async with self.db.session_maker() as session:
            async with session.begin():
                location = Location(
                    lat=lat,
                    lng=lng,
                    title=title,
                    type=type_,
                    address=address,
                    time_start=time_start,
                    time_end=time_end,
                    main_icon=main_icon,
                    building_type=building_type,
                    building_type_name_ru=building_type_name_ru,
                    bounds=[Bounds(lat=b[0], lng=b[1]) for b in bounds]
                )
                session.add(location)
                await session.commit()
                return location.id


repo = MapPointsRepository()


async def test():
    # await repo.add_location(
    #     lat=54.876545,
    #     lng=69.134236,
    #     title="Бассейн СКУ им. М. Козыбаева",
    #     type_="square",
    #     address="Улица Абая Кунанбаева, 31а",
    #     time_start="ПН-ПТ",
    #     time_end="7:00-20:00",
    #     main_icon=None,
    #     bounds=[(54.876976, 69.134204), (54.87663, 69.133618), (54.876192, 69.134321), (54.876501, 69.134962)]
    # )
    #
    # await repo.add_location(
    #     lat=54.875406,
    #     lng=69.135137,
    #     title="Kozybaev University, приемная комиссия",
    #     type_="square",
    #     address="СКУ им. М. Козыбаева, улица Магжана Жумабаева, 114, Петропавловск",
    #     time_start="ПН-ПТ",
    #     time_end="7:00-20:00",
    #     main_icon=None,
    #     bounds=[(54.875796, 69.135683), (54.875714, 69.135829), (54.875011, 69.134577), (54.87512, 69.134431)]
    # )
    # await repo.add_location(
    #     lat=54.875119,
    #     lng=69.134629,
    #     title="Kozybaev University корпус 5",
    #     type_="square",
    #     address="СКУ им. М. Козыбаева Улица Интернациональная, 26 5 корпус",
    #     time_start="ПН-ПТ",
    #     time_end="09:00-18:00",
    #     main_icon=None,
    #     bounds=[
    #         (54.875559, 69.132989),
    #         (54.875646, 69.133182),
    #         (54.874923, 69.134369),
    #         (54.874824, 69.134197)
    #     ]
    # )
    # image_path = r'E:\PycharmProjects\skgu_diplome_api\src\api\locations\assets\people-at-the-table-svgrepo-com.svg'
    # await repo.add_location(
    #     lat=54.875119,
    #     lng=69.134629,
    #     title="Kozybaev University корпус 5",
    #     type_="square",
    #     address="СКУ им. М. Козыбаева Улица Интернациональная, 26 5 корпус",
    #     time_start="ПН-ПТ",
    #     time_end="09:00-18:00",
    #     building_type_name_ru="тест",
    #     building_type="тест",
    #     main_icon=image_to_base64(image_path),
    #     bounds=[
    #         (54.875559, 69.132989),
    #         (54.875646, 69.133182),
    #         (54.874923, 69.134369),
    #         (54.874824, 69.134197)
    #     ]
    # )
    # pass
    # image_path = r'E:\PycharmProjects\skgu_diplome_api\src\api\locations\assets\people-at-the-table-svgrepo-com.svg'
    # await repo.add_location(
    #     lat=54.875119,
    #     lng=69.134629,
    #     title="Kozybaev University корпус 4",
    #     type_="square",
    #     address="СКУ им. М. Козыбаева Улица Александра Пушкина, 81",
    #     time_start="ПН-ПТ",
    #     time_end="09:00-18:00",
    #     building_type_name_ru="Учебные корпуса",
    #     building_type="academic_building",
    #     main_icon=image_to_base64(image_path),
    #     bounds=[
    #         (54.876096, 69.132633),
    #         (54.876295, 69.132163),
    #         (54.875745, 69.131098),
    #         (54.87564, 69.131282)
    #     ]
    # )
    # image_path = r'E:\PycharmProjects\skgu_diplome_api\src\api\locations\assets\people-at-the-table-svgrepo-com.svg'
    # await repo.add_location(
    #     lat=54.877201,
    #     lng=69.13214,
    #     title="Kozybaev University корпус 3",
    #     type_="square",
    #     address="СКУ им. М. Козыбаева улица Александра Пушкина, 86",
    #     time_start="ПН-ПТ",
    #     time_end="09:00-18:00",
    #     building_type_name_ru="Учебные корпуса",
    #     building_type="academic_building",
    #     main_icon=image_to_base64(image_path),
    #     bounds=[
    #         (54.877556, 69.132422),
    #         (54.87737, 69.132728),
    #         (54.876855, 69.131753),
    #         (54.877038, 69.131455)
    #     ]
    # )
    image_path = r'E:\PycharmProjects\skgu_diplome_api\src\api\locations\assets\people-at-the-table-svgrepo-com.svg'
    await repo.add_location(
        lat=54.878436,
        lng=69.132768,
        title="Kozybaev University корпус 1",
        type_="square",
        address="СКУ им. М. Козыбаева Улица Абая Кунанбаева, 18",
        time_start="ПН-ПТ",
        time_end="09:00-18:00",
        building_type_name_ru="Учебные корпуса",
        building_type="academic_building",
        main_icon=image_to_base64(image_path),
        bounds=[
            (54.87876, 69.132715),
            (54.878492, 69.133246),
            (54.878118, 69.132543),
            (54.878464, 69.132162)
        ]
    )
    pass


if __name__ == '__main__':
    asyncio.run(test())
