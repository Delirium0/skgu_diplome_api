from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import datetime
import asyncio
import chardet
import requests
from requests_ntlm import HttpNtlmAuth

from config import PASSWORD, TEST_MODE  # Ensure config.py with PASSWORD is in the same directory or accessible
from src.api.schedule.parsing_utils import parse_student_info_from_html, parse_exams_table
from src.api.schedule.schedule import parse_schedule_from_page, get_current_lesson
from src.api.schedule.utils import parsing_evaluations, parsing_user_id, parsing_rating_group

router = APIRouter(prefix='/schedule')


async def fetch_content_with_ntlm_auth(url: str, user_login: str, user_pass: str) -> str:
    domain = ''
    session = requests.Session()
    session.auth = HttpNtlmAuth(domain + '\\' + user_login, user_pass)
    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        encoding = chardet.detect(response.content)['encoding']
        decoded_content = response.content.decode(encoding)
        return decoded_content
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from URL: {e}")
    except UnicodeDecodeError as e:
        print(f"Decoding error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to decode content: {e}")


@router.post("/schedule/", response_model=Dict)
async def get_schedule_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/ratingviewing.asp'
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    student_info = await parse_student_info_from_html(content)
    print(student_info)
    if student_info is None:
        return {"results": None}
    await asyncio.sleep(1)
    schedule_url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year={student_info.get("year")}&Semester={student_info.get("semester")}&IDStudent={student_info.get("student_id")}&iFlagStudent=0'

    if TEST_MODE == '1':
        schedule_url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year={student_info.get("year")}&Semester=1&IDStudent={student_info.get("student_id")}&iFlagStudent=0'
        print(schedule_url)
    content_schedule = await fetch_content_with_ntlm_auth(schedule_url, user_login, user_pass)

    schedule_data = parse_schedule_from_page(content_schedule)

    if schedule_data is None:
        raise HTTPException(status_code=400, detail="Failed to parse schedule or schedule not found.")
    return {"results": schedule_data}


@router.post("/exams_evaluations/", response_model=Dict)
async def get_exams_evaluations_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    url = 'https://is.ku.edu.kz/e-Rectorat/Services/Cabinet/Student/Notes.asp'
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    result = await parse_exams_table(content)
    return {"results": result}


@router.post("/evaluations/", response_model=List[Dict])
async def get_evaluations_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    if TEST_MODE == '2':
        test_data = [
            {
                "1": "100",
                "2": "100",
                "3": "80",
                "4": "100",
                "5": "100",
                "6": "100",
                "7": "",
                "8": "",
                "9": "",
                "10": "100|100",
                "11": "",
                "12": "100|100",
                "13": "",
                "14": "",
                "15": "100|100|100",
                "subject_name": "Информационная безопасность",
                "teacher": "преподаватель: Кухаренко Евгения Владимировна",
                "average_grade": "98"
            },
            {
                "1": "",
                "2": "",
                "3": "95|85|84",
                "4": "",
                "5": "",
                "6": "70|70|70|90",
                "7": "",
                "8": "",
                "9": "70|90|75|75|58",
                "10": "",
                "11": "",
                "12": "90|90|90|72",
                "13": "",
                "14": "",
                "15": "0|0|87",
                "subject_name": "Проектирование программного обеспечения",
                "teacher": "преподаватель: Ушакова Екатерина Вячеславовна",
                "average_grade": "72"
            },
            {
                "1": "",
                "2": "",
                "3": "91|70|88|68",
                "4": "",
                "5": "",
                "6": "90|85|100|100",
                "7": "",
                "8": "",
                "9": "81|100|100|100",
                "10": "",
                "11": "",
                "12": "57|90|100",
                "13": "",
                "14": "",
                "15": "0|80|80|80",
                "subject_name": "Системы искусственного интеллекта",
                "teacher": "преподаватель: Астапенко Наталья Владимировна",
                "average_grade": "82"
            },
            {
                "1": "",
                "2": "",
                "3": "100|0",
                "4": "",
                "5": "",
                "6": "99|100",
                "7": "",
                "8": "",
                "9": "100|100",
                "10": "",
                "11": "",
                "12": "100|100",
                "13": "",
                "14": "",
                "15": "0|0",
                "subject_name": "Теория и практика создания интерактивных приложений",
                "teacher": "преподаватель: Куликов Владимир Павлович",
                "average_grade": "70"
            },
            {
                "1": "",
                "2": "",
                "3": "",
                "4": "0",
                "5": "",
                "6": "100|100",
                "7": "95",
                "8": "94|96",
                "9": "95",
                "10": "97",
                "11": "91",
                "12": "",
                "13": "90",
                "14": "95",
                "15": "70|98",
                "subject_name": "Тестирование и обеспечение качества программного обеспечения",
                "teacher": "преподаватель: Лисянов Владимир Валерьевич",
                "average_grade": "86"
            }
        ]
        return test_data
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/ratingviewing.asp'
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    student_info = await parse_student_info_from_html(content)
    print(student_info)
    if student_info is None:
        return {"results": None}
    await asyncio.sleep(1)
    evaluations_url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year={student_info.get("year")}&Semester={student_info.get("semester")}&IDStudent={student_info.get("student_id")}&iFlagStudent=0'

    if TEST_MODE == '1':
        evaluations_url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year={student_info.get("year")}&Semester=1&IDStudent={student_info.get("student_id")}&iFlagStudent=0'

    content_evaluations = await fetch_content_with_ntlm_auth(evaluations_url, user_login, user_pass)

    evaluations_data = await parsing_evaluations(content_evaluations)

    if evaluations_data is None:
        raise HTTPException(status_code=400, detail="Failed to parse schedule or schedule not found.")
    return evaluations_data


@router.post("/user_id/", response_model=Dict)
async def get_user_id_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/ratingviewing.asp'
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    user_id = await parsing_user_id(content)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User ID not found.")
    return {"results": user_id}


@router.post("/current_lesson/", response_model=Optional[Dict])
async def get_current_lesson_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    url = f'https://is.ku.edu.kz/e-Rectorat/controls/ac_schedule_out.asp?Opera=4&Faculty=0&EduForm=0&Group=6207&Chair=0&Year=2024&Semester=1&Period=11.11.2024&Curs=0&isLangRu=0&IDTeacher=0&Speciality=0'  # Replace with dynamic group if needed
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    schedule_data = parse_schedule_from_page(content)
    if schedule_data is None:
        raise HTTPException(status_code=400, detail="Failed to parse schedule or schedule not found.")
    current_lesson = get_current_lesson(
        {"results": schedule_data})  # Wrap schedule_data in a dict to match get_current_lesson expectation
    return current_lesson


@router.post("/group_rating/", response_model=List[Dict])
async def get_group_rating_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingGroup.asp?Year=2024&Semester=1&IDGroup=6207&iFlagStudent=1'  # Replace with dynamic group ID if needed
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    rating_group = await parsing_rating_group(content)
    return rating_group
