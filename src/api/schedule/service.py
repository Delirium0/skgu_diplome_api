import asyncio

import chardet
import requests
from requests_ntlm import HttpNtlmAuth

from config import PASSWORD
from src.api.schedule.schedule import parse_schedule_from_page, get_current_lesson
from src.api.schedule.utils import parsing_evaluations, parsing_user_id


async def get_user_evaluations(user_id: int) -> list[dict]:
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year=2024&Semester=1&IDStudent={user_id}&iFlagStudent=1'

    domain = ''
    username = 'VT1042'
    password = PASSWORD
    session = requests.Session()
    session.auth = HttpNtlmAuth(domain + '\\' + username, password)

    response = session.get(url)

    # Определение кодировки текста с помощью chardet
    encoding = chardet.detect(response.content)['encoding']

    try:
        decoded_content = response.content.decode(encoding)
        # with open('saved_content.txt', 'r', encoding='utf-8') as file:
        #     decoded_content = file.read()  # читаем содержимое файла
        result = await parsing_evaluations(decoded_content)
        print(result)
        return result
    except UnicodeDecodeError:
        print(f"Ошибка декодирования с использованием кодировки: {encoding}")


async def get_user_id(user_login: str, user_pass) -> dict:
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/ratingviewing.asp'

    domain = ''

    session = requests.Session()
    session.auth = HttpNtlmAuth(domain + '\\' + user_login, user_pass)

    response = session.get(url)

    # Определение кодировки текста с помощью chardet
    encoding = chardet.detect(response.content)['encoding']

    try:
        decoded_content = response.content.decode(encoding)

        result = await parsing_user_id(decoded_content)
        print(result)
        return {"results": result}
    except UnicodeDecodeError:
        print(f"Ошибка декодирования с использованием кодировки: {encoding}")


async def schedule(user_login: str, user_pass: str) -> dict:
    url = f'https://is.ku.edu.kz/e-Rectorat/controls/ac_schedule_out.asp?Opera=4&Faculty=0&EduForm=0&Group=6207&Chair=0&Year=2024&Semester=1&Period=11.11.2024&Curs=0&isLangRu=0&IDTeacher=0&Speciality=0'

    domain = ''

    session = requests.Session()
    session.auth = HttpNtlmAuth(domain + '\\' + user_login, user_pass)

    response = session.get(url)

    # Определение кодировки текста с помощью chardet
    encoding = chardet.detect(response.content)['encoding']

    try:
        decoded_content = response.content.decode(encoding)

        result = parse_schedule_from_page(decoded_content)
        # for hz, hz333 in result.items():
        #     print(hz, hz333)
        return {"results": result}
    except UnicodeDecodeError:
        print(f"Ошибка декодирования с использованием кодировки: {encoding}")



if __name__ == '__main__':
    pass