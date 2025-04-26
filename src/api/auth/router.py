import asyncio
import time
import os  # Пример для ключа шифрования, если бы он использовался

from fastapi import APIRouter, Response, HTTPException, Depends, Request
from pydantic import BaseModel
import aiolimiter  # Для rate limiting

# --- ЗАВИСИМОСТИ ВАШЕГО ПРОЕКТА (Замените на ваши реальные пути) ---
# Предполагается, что эти модули существуют и настроены
from src.api.auth.security import security, config, \
    pwd_context  # pwd_context пока оставляем, но verify использовать не будем для plaintext
from src.api.auth.user_repo import user_repository  # Должен уметь сохранять поле 'password' как строку
from src.api.schedule.parsing_utils import auth_check  # Убедитесь, что этот импорт корректен
from src.api.schedule.router import fetch_content_with_ntlm_auth  # Функция вызова внешнего API

# --------------------------------------------------------------------

# --- Настройка Rate Limiter ---
# 1 вызов в 1 секунду. Глобальный для всего приложения.
external_api_limiter = aiolimiter.AsyncLimiter(1, 1)
# -----------------------------

# --- Настройка Кэша Неудачных Попыток ---
# Простой кэш в памяти (для продакшена лучше Redis/Memcached)
# Ключ: f"{login}::{password}", Значение: timestamp истечения кэша
failed_auth_cache = {}
FAILED_CACHE_TTL = 60  # секунд (кэшируем неудачу на 1 минуту)
# -----------------------------------------

router = APIRouter(prefix='/auth', tags=["Auth"])


class UserLoginSchema(BaseModel):
    login: str
    password: str  # Принимаем пароль в открытом виде


@router.post('/login')
async def login(creds: UserLoginSchema, response: Response):
    """
    Эндпоинт для входа пользователя.
    Проверяет локальную базу данных, затем внешний API (с rate limiting и кэшированием неудач).
    ВНИМАНИЕ: В текущей версии хранит и сравнивает пароли в ОТКРЫТОМ ВИДЕ локально!
    """
    print(f"Login attempt for: {creds.login}")

    user = await user_repository.get_user_by_username(creds.login)

    # --- 1. Попытка локальной аутентификации (сравнение открытых паролей) ---
    if user and hasattr(user, 'password') and user.password == creds.password:
        print(f"Local plaintext auth SUCCESS for {creds.login}")
        # Пароль совпал локально, выдаем токен без обращения к внешнему API
        data = {"role": user.role}
        token = security.create_access_token(uid=str(user.id), data=data)
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {'access_token': token, 'source': 'local'}

    # --- Локальная аутентификация не удалась (нет юзера или пароль не совпал) ---
    print(f"Local plaintext auth FAILED or user not found for {creds.login}. Proceeding to external check.")

    # --- 2. Проверка кэша НЕУДАЧНЫХ внешних попыток ---
    cache_key = f"{creds.login}::{creds.password}"  # Уникальный ключ для комбинации
    current_time = time.monotonic()

    # Простая очистка старого кэша (можно вынести в фоновую задачу)
    keys_to_delete = [k for k, v in failed_auth_cache.items() if v < current_time]
    for k in keys_to_delete:
        try:
            del failed_auth_cache[k]
        except KeyError:
            pass  # Уже удален другим запросом

    if cache_key in failed_auth_cache and failed_auth_cache[cache_key] > current_time:
        print(f"Cached external auth FAILURE for {creds.login}")
        raise HTTPException(status_code=401, detail="Invalid credentials (cached failure)")
    # ----------------------------------------------------

    # --- 3. Обращение к ВНЕШНЕМУ API с Rate Limiting ---
    auth_url = 'https://is.ku.edu.kz/e-Rectorat/Services/Cabinet/Student/Notes.asp'
    is_auth = False
    print(f"Attempting to acquire rate limit lock for external auth for {creds.login}...")
    async with external_api_limiter:
        # Мы получили "слот" для выполнения запроса
        print(f"Rate limit lock acquired for {creds.login} at {time.time()}. Calling external API.")
        try:
            # Повторно проверяем кэш на случай, если другой запрос добавил запись, пока мы ждали лимитер
            if cache_key in failed_auth_cache and failed_auth_cache[cache_key] > time.monotonic():
                print(f"Cached external auth FAILURE found for {creds.login} *after* acquiring lock.")
                raise HTTPException(status_code=401, detail="Invalid credentials (cached failure)")

            is_auth = await fetch_content_with_ntlm_auth(auth_url, creds.login, creds.password)

        except HTTPException as e:
            # Если кэш сработал внутри лимитера
            raise e
        except Exception as e:
            # Ошибка при вызове внешнего API
            print(f"External auth error for {creds.login}: {e}")
            # Не кэшируем системные ошибки внешнего сервиса, только неудачи аутентификации
            raise HTTPException(status_code=503, detail="External authentication service unavailable or failed")

    # --- 4. Обработка результата внешнего API ---
    if not is_auth:
        print(f"External auth FAILED for {creds.login}. Caching failure.")
        # Кэшируем неудачную попытку
        failed_auth_cache[cache_key] = time.monotonic() + FAILED_CACHE_TTL
        raise HTTPException(status_code=401, detail="Invalid credentials (external check failed)")

    # --- Внешняя аутентификация УСПЕШНА ---
    print(f"External auth SUCCESS for {creds.login}")

    # Если пользователь не был найден локально ранее, создаем его
    if not user:
        print(f"User {creds.login} not found locally. Creating user...")
        # ВНИМАНИЕ: СОХРАНЕНИЕ ПАРОЛЯ В ОТКРЫТОМ ВИДЕ!
        user_data = {
            "login": creds.login,
            "password": creds.password,
            "role": "user",
        }
        try:
            user = await user_repository.create_user(user_data)

            if not user or not user.id:
                print(f"Failed to get user object after creation for {creds.login}")
                raise HTTPException(status_code=500,
                                    detail="Could not create user record after successful external auth")
            print(f"User {creds.login} created locally with ID: {user.id}")
        except Exception as e:
            # Выводим полное исключение для лучшей диагностики
            import traceback
            print(f"Failed to create local user record for {creds.login}: {e}")
            print(traceback.format_exc())  # Печатаем traceback
            raise HTTPException(status_code=500, detail="Could not create user record")
    # else:
    # Если пользователь существовал, но локальный пароль не совпал,
    # можно было бы обновить пароль в БД на тот, что прошел внешнюю проверку.
    # Но так как это открытый текст, возможно, лучше этого не делать автоматически.
    # await user_repository.update_user_password(user.id, creds.password) # Примерно так
    # print(f"User {creds.login} existed locally, external auth successful (potential password update needed/skipped).")
    # pass # Просто используем существующий объект user

    # --- 5. Выдача токена ---
    # Сюда попадаем, если:
    # 1. Локальная аутентификация провалилась, но внешняя прошла (и пользователь создан/найден).
    if not user or not user.id:
        # Дополнительная проверка на всякий случай
        print(f"Error: User object is missing before token generation for {creds.login}")
        raise HTTPException(status_code=500, detail="User data inconsistency")

    print(f"Generating token for user {user.login} (ID: {user.id}, Role: {user.role})")
    data = {"role": user.role}
    token = security.create_access_token(uid=str(user.id), data=data)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)

    return {'access_token': token, 'source': 'external'}

# --- Пример функции создания админа (если нужно) ---
# Учтите, что пароль здесь тоже будет в открытом виде, если следовать логике выше
# async def create_admin():
#     # ВНИМАНИЕ: ПАРОЛЬ В ОТКРЫТОМ ВИДЕ!
#     admin_password = "admin_password_plain" # Замените на реальный пароль
#     admin_data = {
#         "login": "admin",
#         "password": admin_password, # Сохраняем как есть
#         "role": "admin"
#     }
#     existing_admin = await user_repository.get_user_by_username("admin")
#     if not existing_admin:
#         await user_repository.create_user(**admin_data)
#         print("Admin user created with plaintext password.")
#     else:
#         print("Admin user already exists.")

# if __name__ == '__main__':
#     # Запуск создания админа (если требуется при старте)
#     # asyncio.run(create_admin())
#     print("Auth router script loaded.")
#     # Обычно этот файл не запускается через if __name__ == '__main__' в FastAPI,
#     # а импортируется основным приложением.
