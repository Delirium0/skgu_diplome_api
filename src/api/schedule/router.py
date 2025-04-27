import traceback
import time  # Добавлено для логирования (опционально)

from fastapi import APIRouter, Depends
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import datetime
import asyncio
import chardet
import requests
from requests_ntlm import HttpNtlmAuth

# --- Импорт зависимостей ---
from config import PASSWORD, TEST_MODE
from src.api.auth.security import security
from src.api.auth.service import get_current_user
from src.api.auth.user_repo import user_repository
from src.api.limiter import external_api_limiter
from src.api.schedule.parsing_utils import parse_student_info_from_html, parse_exams_table, \
    parser_student_info_schedule_from_html, create_schedule_url_fstring_unsafe
from src.api.schedule.schedule import parse_schedule_from_page, get_current_lesson
from src.api.schedule.utils import parsing_evaluations, parsing_user_id, parsing_rating_group

# --- ИМПОРТ ОБЩЕГО ЛИМИТЕРА ---
# ------------------------------

router = APIRouter(prefix='/schedule', tags=["Schedule"])


# Важно: Сама функция fetch_content_with_ntlm_auth НЕ должна содержать лимитер.
# Лимитер применяется ПЕРЕД ее вызовом.
async def fetch_content_with_ntlm_auth(url: str, user_login: str, user_pass: str) -> str | bool:
    if TEST_MODE == '1':
        # В тестовом режиме имитируем успешный ответ без реального запроса
        # Можно вернуть пример HTML или просто True/пустую строку, если контент не важен для теста
        print(f"[TEST_MODE 1] Skipping external call for {url}")
        # Для эндпоинта /schedule/ может понадобиться тестовый HTML
        # return "<html><body>Test Schedule Data</body></html>"
        return ""  # Или True, если логика вызывающей стороны это обработает
    if TEST_MODE == '2':
        # Аналогично для TEST_MODE 2, если он тоже обходит внешний вызов
        print(f"[TEST_MODE 2] Skipping external call for {url}")
        # return "<html><body>Test Data Mode 2</body></html>"
        return ""  # Или True

    # Если не тестовый режим, выполняем реальный запрос
    domain = ''
    session = requests.Session()
    session.auth = HttpNtlmAuth(domain + '\\' + user_login, user_pass)
    try:
        # Используем requests синхронно, но будем вызывать эту async функцию через run_in_executor
        # или использовать асинхронный HTTP клиент (httpx) для полной асинхронности
        # Пока оставляем requests, но имеем в виду потенциальную блокировку

        # ----- Блок с Rate Limiter ПЕРЕД СИНХРОННЫМ ВЫЗОВОМ -----
        # ПРИМЕЧАНИЕ: Применение aiolimiter перед синхронным requests не так эффективно,
        # как перед асинхронным вызовом (например, с httpx), так как сам вызов requests
        # может блокировать event loop. Но это ограничит ЧАСТОТУ попыток блокировки.
        print(f"[{time.time():.4f}] Schedule: Attempting lock for {url}...")
        async with external_api_limiter:
            print(f"[{time.time():.4f}] Schedule: Lock acquired for {url}. Making request...")
            try:
                # Выполнение синхронного запроса
                response = await asyncio.to_thread(session.get, url)  # Запуск синхронной функции в потоке
                response.raise_for_status()
                encoding = chardet.detect(response.content)['encoding'] or 'utf-8'  # Добавим fallback encoding
                decoded_content = response.content.decode(encoding)
                print(f"[{time.time():.4f}] Schedule: Request finished for {url}.")
                return decoded_content
            except requests.exceptions.HTTPError as e:
                print(f"[{time.time():.4f}] Schedule: HTTP Error during request for {url}: {e.response.status_code}")
                if e.response.status_code == 401:
                    print("Ошибка авторизации (401 Unauthorized)")
                    return False
                else:
                    print(f"HTTP error: {e}")
                    raise HTTPException(status_code=e.response.status_code,
                                        detail=f"Failed to fetch data from URL: {e}")
            except requests.exceptions.RequestException as e:
                print(f"[{time.time():.4f}] Schedule: Request Error for {url}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to fetch data from URL: {e}")
            except UnicodeDecodeError as e:
                print(f"[{time.time():.4f}] Schedule: Decoding Error for {url}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to decode content: {e}")
            finally:
                print(f"[{time.time():.4f}] Schedule: Lock released for {url}.")
        # --------------------------------------------------
        # Если лимитер не сработал (например, исключение до блока), или если нужно вернуть что-то по умолчанию
        # Эта часть кода не должна достигаться при нормальной работе с лимитером
        # return False # Или другое значение по умолчанию
    except Exception as e:
        print(e)
    # Этот блок кода теперь обрабатывается внутри async with или в except блоках
    # Поэтому старая логика try/except здесь больше не нужна в таком виде.


@router.post("/schedule/", response_model=Dict, dependencies=[Depends(security.access_token_required)])
async def get_schedule_endpoint(current_user=Depends(get_current_user)):
    url = f'https://is.ku.edu.kz/e-Rectorat/controls/ac_schedule_out.asp'
    user_login = current_user.login
    # ПРЕДУПРЕЖДЕНИЕ: Хранение пароля в current_user.password_no_hash небезопасно!
    user_pass = current_user.password_no_hash

    if TEST_MODE == '2':
        # Ваш тестовый режим остается без изменений
        # ... (код для TEST_MODE == '2') ...
        return {"results": []}  # Пример возврата

    student_info = {}
    # Получение первичной информации для определения параметров запроса расписания
    if current_user.group_id is None or current_user.cmbPeriod is None or current_user.semester is None or current_user.year is None:
        print(f"[{time.time():.4f}] Schedule: Fetching initial student info for {user_login}...")
        # --- Применяем лимитер ПЕРЕД вызовом ---
        content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
        # --------------------------------------
        if content is False:  # Проверяем на ошибку 401
            raise HTTPException(status_code=401, detail="Authentication failed fetching initial student info.")
        if not content:  # Проверяем на другие ошибки или пустой ответ
            raise HTTPException(status_code=503, detail="Failed to fetch initial student info content.")

        student_info = await parser_student_info_schedule_from_html(content)
        if not student_info:
            raise HTTPException(status_code=404, detail="Could not parse student info from initial page.")

        cmbPeriod = student_info.get('cmbPeriod')
        cmbPeriod_date = None
        if cmbPeriod:
            try:
                cmbPeriod_date = datetime.datetime.strptime(cmbPeriod, '%d.%m.%Y').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format for cmbPeriod.")

        user_update_info = {
            'group_id': int(student_info.get('cmbGroup', 0)),  # Добавим default
            'cmbPeriod': cmbPeriod_date,
            'semester': int(student_info.get('cmbSemester', 0)),  # Добавим default
            'year': int(student_info.get('cmbYear', 0)),  # Добавим default
        }
        # Проверим, что значения не нулевые, если они обязательны
        if not all(user_update_info.values()):
            print(f"Warning: Missing some student info fields: {user_update_info}")
            # Можно либо падать, либо использовать дефолты, если возможно

        await user_repository.update_user(current_user.id, user_update_info)
        print(f"[{time.time():.4f}] Schedule: Updated student info for {user_login}: {user_update_info}")
        # Обновляем student_info для использования ниже
        student_info = {
            'cmbYear': user_update_info['year'],
            'cmbPeriod': cmbPeriod,  # Используем исходную строку для URL
            'cmbSemester': user_update_info['semester'],
            'cmbGroup': user_update_info['group_id']
        }

    else:
        # Используем данные из current_user
        student_info = {
            'cmbYear': current_user.year,
            'cmbPeriod': f'{current_user.cmbPeriod.strftime("%d.%m.%Y")}' if current_user.cmbPeriod else None,
            # Форматируем дату обратно в строку
            'cmbSemester': current_user.semester,
            'cmbGroup': current_user.group_id
        }
        print(f"[{time.time():.4f}] Schedule: Using cached student info for {user_login}: {student_info}")

    # Формируем URL для конкретного расписания
    schedule_url_fstring = await create_schedule_url_fstring_unsafe(url, student_info)
    if not schedule_url_fstring:
        raise HTTPException(status_code=400, detail="Could not create schedule URL. Missing required parameters.")

    print(f"[{time.time():.4f}] Schedule: Fetching actual schedule for {user_login} from {schedule_url_fstring}...")

    # --- УДАЛИТЬ ЭТОТ SLEEP ---
    # await asyncio.sleep(1)
    # -------------------------

    # --- Применяем лимитер ПЕРЕД вызовом ---
    content = await fetch_content_with_ntlm_auth(schedule_url_fstring, user_login, user_pass)
    # --------------------------------------
    if content is False:  # Проверяем на ошибку 401
        raise HTTPException(status_code=401, detail="Authentication failed fetching schedule.")
    if not content:  # Проверяем на другие ошибки или пустой ответ
        raise HTTPException(status_code=503, detail="Failed to fetch schedule content.")

    results = parse_schedule_from_page(content)
    print(f"[{time.time():.4f}] Schedule: Parsed schedule for {user_login}. Found {len(results)} items.")
    return {"results": results}


# --- Аналогично добавляем лимитер в другие эндпоинты, где есть fetch_content_with_ntlm_auth ---

@router.post("/exams_evaluations/", response_model=Dict)
async def get_exams_evaluations_endpoint(current_user=Depends(get_current_user)):
    user_login = current_user.login
    user_pass = current_user.password_no_hash

    # ВНИМАНИЕ: Этот эндпоинт не использует Depends(get_current_user)
    # Передача пароля в Query параметрах - КРАЙНЕ НЕБЕЗОПАСНО!
    # Рекомендуется переделать на использование токена и Depends(get_current_user)
    url = 'https://is.ku.edu.kz/e-Rectorat/Services/Cabinet/Student/Notes.asp'
    print(f"[{time.time():.4f}] ExamsEval: Fetching for {user_login}...")
    # --- Применяем лимитер ПЕРЕД вызовом ---
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    # --------------------------------------
    if content is False: raise HTTPException(status_code=401, detail="Authentication failed.")
    if not content: raise HTTPException(status_code=503, detail="Failed to fetch content.")

    result = await parse_exams_table(content)
    print(f"[{time.time():.4f}] ExamsEval: Parsed for {user_login}.")
    return {"results": result}


@router.post("/evaluations/", response_model=List[Dict], dependencies=[Depends(security.access_token_required)])
async def get_evaluations_endpoint(current_user=Depends(get_current_user)):
    user_login = current_user.login
    user_pass = current_user.password_no_hash  # НЕБЕЗОПАСНО!
    if TEST_MODE == '2':
        return []  # Пример

    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/ratingviewing.asp'
    student_info = {}
    if current_user.student_id is None:
        print(f"[{time.time():.4f}] Evaluations: Fetching initial student ID for {user_login}...")
        # --- Применяем лимитер ПЕРЕД вызовом ---
        content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
        # --------------------------------------
        if content is False: raise HTTPException(status_code=401, detail="Authentication failed fetching student ID.")
        if not content: raise HTTPException(status_code=503, detail="Failed to fetch student ID content.")

        student_info = await parse_student_info_from_html(content)
        if not student_info or 'student_id' not in student_info:
            raise HTTPException(status_code=404, detail="Could not parse student ID from page.")

        user_update_info = {'student_id': int(student_info.get('student_id'))}
        await user_repository.update_user(current_user.id, user_update_info)
        # Обновляем student_info для использования ниже
        student_info = {  # Собираем нужные данные для URL оценок
            'year': student_info.get('year', current_user.year),  # Нужны год и семестр для URL
            'semester': student_info.get('semester', current_user.semester),
            'student_id': user_update_info['student_id'],
        }
        # Обновляем объект current_user, если он используется дальше
        current_user.student_id = user_update_info['student_id']

    else:
        student_info = {
            'year': current_user.year,
            'semester': current_user.semester,
            'student_id': current_user.student_id,
        }
        print(f"[{time.time():.4f}] Evaluations: Using cached student ID {current_user.student_id} for {user_login}")

    await asyncio.sleep(1)
    print(student_info)

    evaluations_url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year={student_info.get("year")}&Semester={student_info.get("semester")}&IDStudent={student_info.get("student_id")}&iFlagStudent=0'

    if TEST_MODE == '1':
        evaluations_url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingViewingPrint.asp?Year={student_info.get("year")}&Semester=1&IDStudent={student_info.get("student_id")}&iFlagStudent=0'
        print(f"[{time.time():.4f}] Evaluations: Using TEST_MODE 1 URL: {evaluations_url}")
    else:
        print(f"[{time.time():.4f}] Evaluations: Using URL: {evaluations_url}")

    print(f"[{time.time():.4f}] Evaluations: Fetching actual evaluations for {user_login}...")
    # --- Применяем лимитер ПЕРЕД вызовом ---
    content_evaluations = await fetch_content_with_ntlm_auth(evaluations_url, user_login, user_pass)
    # --------------------------------------
    if content_evaluations is False: raise HTTPException(status_code=401,
                                                         detail="Authentication failed fetching evaluations.")
    if not content_evaluations: raise HTTPException(status_code=503, detail="Failed to fetch evaluations content.")

    evaluations_data = await parsing_evaluations(content_evaluations)

    if evaluations_data is None:  # parse_evaluations должна вернуть [] при отсутствии данных, а не None? Уточнить.
        print(f"[{time.time():.4f}] Evaluations: Parsing returned None for {user_login}.")
        # Может быть не ошибка, а просто нет оценок?
        # raise HTTPException(status_code=400, detail="Failed to parse evaluations or evaluations not found.")
        return []  # Возвращаем пустой список, если парсер вернул None

    print(f"[{time.time():.4f}] Evaluations: Parsed for {user_login}. Found {len(evaluations_data)} subjects.")
    return evaluations_data


@router.post("/user_id/", response_model=Dict)
async def get_user_id_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    # СНОВА ПРЕДУПРЕЖДЕНИЕ О НЕБЕЗОПАСНОСТИ ПЕРЕДАЧИ ПАРОЛЯ В QUERY!
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/ratingviewing.asp'
    print(f"[{time.time():.4f}] UserID: Fetching for {user_login}...")
    # --- Применяем лимитер ПЕРЕД вызовом ---
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    # --------------------------------------
    if content is False: raise HTTPException(status_code=401, detail="Authentication failed.")
    if not content: raise HTTPException(status_code=503, detail="Failed to fetch content.")

    user_id = await parsing_user_id(content)  # Убедитесь, что эта функция парсит ID корректно
    if user_id is None:
        raise HTTPException(status_code=404, detail="User ID not found on page.")
    print(f"[{time.time():.4f}] UserID: Parsed ID {user_id} for {user_login}.")
    return {"results": user_id}


@router.post("/current_lesson/", response_model=Optional[Dict])
async def get_current_lesson_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    # СНОВА ПРЕДУПРЕЖДЕНИЕ О НЕБЕЗОПАСНОСТИ ПЕРЕДАЧИ ПАРОЛЯ В QUERY!
    # TODO: Сделать URL динамическим на основе данных пользователя (group_id, year, semester, period)
    # Этот URL выглядит захардкоженным!
    url = f'https://is.ku.edu.kz/e-Rectorat/controls/ac_schedule_out.asp?Opera=4&Faculty=0&EduForm=0&Group=6207&Chair=0&Year=2024&Semester=1&Period=11.11.2024&Curs=0&isLangRu=0&IDTeacher=0&Speciality=0'
    print(f"[{time.time():.4f}] CurrentLesson: Fetching schedule for {user_login} using URL: {url}...")
    # --- Применяем лимитер ПЕРЕД вызовом ---
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    # --------------------------------------
    if content is False: raise HTTPException(status_code=401, detail="Authentication failed.")
    if not content: raise HTTPException(status_code=503, detail="Failed to fetch schedule content.")

    schedule_data = parse_schedule_from_page(content)
    if schedule_data is None:
        # raise HTTPException(status_code=400, detail="Failed to parse schedule or schedule not found.")
        return None  # Или вернуть ошибку, если расписание обязательно должно быть

    current_lesson = get_current_lesson({"results": schedule_data})
    print(f"[{time.time():.4f}] CurrentLesson: Found lesson for {user_login}: {current_lesson}")
    return current_lesson


@router.post("/group_rating/", response_model=List[Dict])
async def get_group_rating_endpoint(user_login: str = Query(...), user_pass: str = Query(...)):
    # СНОВА ПРЕДУПРЕЖДЕНИЕ О НЕБЕЗОПАСНОСТИ ПЕРЕДАЧИ ПАРОЛЯ В QUERY!
    # TODO: Сделать URL динамическим (IDGroup, Year, Semester)
    url = f'https://is.ku.edu.kz/E-Rectorat/ratings/RatingGroup.asp?Year=2024&Semester=1&IDGroup=6207&iFlagStudent=1'
    print(f"[{time.time():.4f}] GroupRating: Fetching for {user_login} using URL: {url}...")
    # --- Применяем лимитер ПЕРЕД вызовом ---
    content = await fetch_content_with_ntlm_auth(url, user_login, user_pass)
    # --------------------------------------
    if content is False: raise HTTPException(status_code=401, detail="Authentication failed.")
    if not content: raise HTTPException(status_code=503, detail="Failed to fetch group rating content.")

    rating_group = await parsing_rating_group(content)
    if rating_group is None:
        # raise HTTPException(status_code=400, detail="Failed to parse group rating.")
        return []  # Возвращаем пустой список, если парсер вернул None

    print(f"[{time.time():.4f}] GroupRating: Parsed for {user_login}. Found {len(rating_group)} students.")
    return rating_group
