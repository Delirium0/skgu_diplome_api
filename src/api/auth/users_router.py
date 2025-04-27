# src/api/admin/users_router.py
from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List

# --- Импорты твоего проекта ---
from src.api.auth.models import User # Модель SQLAlchemy
from src.api.auth.user_repo import user_repository # Экземпляр репозитория
from src.api.auth.service import user_is_admin # Зависимость для проверки прав админа
from src.api.auth.security import pwd_context # Для хеширования пароля при обновлении
from .schemas import UserInfoAdmin, UserCreateAdmin, UserUpdateAdmin # Схемы Pydantic

# ------------------------------

# Создаем роутер с префиксом и зависимостью проверки админа для ВСЕХ эндпоинтов в этом роутере
router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Users"],
    dependencies=[Depends(user_is_admin)] # Все эндпоинты требуют прав админа
)

@router.get("/", response_model=List[UserInfoAdmin])
async def get_all_users_admin():
    """
    Получение списка всех пользователей (только для админа).
    Возвращает основную информацию без паролей.
    """
    users = await user_repository.get_all_users()
    # Преобразуем список SQLAlchemy моделей в список Pydantic моделей
    # Используем model_validate для Pydantic v2+ или from_orm для v1
    return [UserInfoAdmin.model_validate(user) for user in users]

@router.get("/{user_id}", response_model=UserInfoAdmin)
async def get_user_admin(user_id: int):
    """
    Получение информации о конкретном пользователе по ID (только для админа).
    """
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return UserInfoAdmin.model_validate(user)

@router.post("/", response_model=UserInfoAdmin, status_code=status.HTTP_201_CREATED)
async def create_user_admin(user_data: UserCreateAdmin):
    """
    Создание нового пользователя (только для админа).
    Пароль передается в открытом виде, репозиторий его хеширует для поля 'password'
    и сохраняет оригинал в 'password_no_hash'.
    """
    # Проверка, не занят ли логин
    existing_user = await user_repository.get_user_by_username(user_data.login)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )

    # Преобразуем Pydantic модель в словарь
    user_dict = user_data.model_dump()

    # Вызываем метод репозитория для создания
    # Репозиторий сам обработает хеширование и password_no_hash
    created_user = await user_repository.create_user(user_dict)

    if not created_user:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось создать пользователя")

    # Возвращаем информацию о созданном пользователе (без паролей)
    return UserInfoAdmin.model_validate(created_user)


@router.put("/{user_id}", response_model=UserInfoAdmin)
async def update_user_admin(user_id: int, user_update_data: UserUpdateAdmin):
    """
    Обновление существующего пользователя (только для админа).
    Позволяет обновлять любые поля, включая пароль (передается в открытом виде).
    """
    # Сначала убедимся, что пользователь существует
    user_to_update = await user_repository.get_user_by_id(user_id)
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # Получаем данные для обновления, исключая непереданные поля (None)
    update_data = user_update_data.model_dump(exclude_unset=True)

    # --- Особая обработка пароля ---
    if "password" in update_data and update_data["password"] is not None:
        plain_password = update_data["password"] # Сохраняем для password_no_hash
        # Хешируем пароль для поля 'password'
        update_data["password"] = pwd_context.hash(plain_password)
        # Добавляем поле 'password_no_hash' для сохранения в репозитории
        update_data["password_no_hash"] = plain_password
    elif "password" in update_data:
         # Если password передан как null или пустая строка (хотя Pydantic не должен пропустить пустую),
         # удаляем его из данных для обновления, чтобы не перезаписать существующий пароль на null
         del update_data["password"]
         # Также удаляем password_no_hash, если он случайно попал
         if "password_no_hash" in update_data:
             del update_data["password_no_hash"]
    # -------------------------------

    # Если нечего обновлять (пришли пустые данные)
    if not update_data:
         return UserInfoAdmin.model_validate(user_to_update) # Возвращаем как есть

    # Вызываем метод репозитория для обновления
    updated_user = await user_repository.update_user(user_id, update_data)

    if not updated_user:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось обновить пользователя")

    # Возвращаем обновленные данные (без паролей)
    return UserInfoAdmin.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(user_id: int, current_admin: User = Depends(user_is_admin)):
    """
    Удаление пользователя по ID (только для админа).
    Админ не может удалить сам себя.
    """
    # Проверка, чтобы админ не удалил сам себя
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете удалить свою учетную запись"
        )

    deleted = await user_repository.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # При успехе возвращаем 204 No Content без тела ответа
    return Response(status_code=status.HTTP_204_NO_CONTENT)