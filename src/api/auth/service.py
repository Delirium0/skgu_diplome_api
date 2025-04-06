import base64
from datetime import date
from typing import Optional, List

from authx.exceptions import JWTDecodeError
from fastapi import APIRouter, Body
from fastapi import Depends
from fastapi import HTTPException, Request
from jose import ExpiredSignatureError
from jwt.exceptions import ExpiredSignatureError
from pydantic import BaseModel, Field, validator, field_validator

from src.api.auth.models import User
from src.api.auth.router import security
from src.api.auth.user_repo import user_repository


async def get_current_user(request: Request) -> User:
    token = None  # Инициализируем токен как None
    # 1. Проверяем заголовок Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]  # Извлекаем токен после "Bearer "

    # 2. Если токен не найден в заголовке, проверяем куки
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = security._decode_token(token)  # Используйте вашу функцию декодирования токена
    except (ExpiredSignatureError, JWTDecodeError):
        raise HTTPException(status_code=401, detail="Token expired. Please refresh your token.")

    user_id = int(payload.sub)
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def user_is_admin(current_user=Depends(get_current_user)):
    print(current_user.role)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only")
    return current_user
