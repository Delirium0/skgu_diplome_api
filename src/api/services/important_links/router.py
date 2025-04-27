from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.services.important_links.important_links_repo import repo_links

# from src.api.important_links.database.models import ImportantLinks #  не нужно импортировать модель сюда, если используем Pydantic схемы

router = APIRouter(prefix='/important_links', tags=["Important Links"])  # Добавил тег для удобства в Swagger


# Pydantic схемы
class ImportantLinkCreate(BaseModel):
    link: str
    link_text: str
    icon: Optional[str] = None


class ImportantLinkUpdate(BaseModel):
    link: Optional[str] = None
    link_text: Optional[str] = None
    icon: Optional[str] = None


class ImportantLinkInfo(BaseModel):
    id: int
    link: str
    link_text: str
    icon: Optional[str] = None

    class Config:
        from_attributes = True  #  Добавьте эту строку


# Эндпоинты

@router.post("/", response_model=ImportantLinkInfo, status_code=201)
async def create_important_link(link_create: ImportantLinkCreate):
    """
    Создает новую важную ссылку.
    """
    link_id = await repo_links.add_link(
        link=link_create.link,
        link_text=link_create.link_text,
        icon=link_create.icon
    )
    important_link = await repo_links.get_link_by_id(link_id)
    if important_link:
        return ImportantLinkInfo.from_orm(
            important_link)  # используем from_orm для преобразования sqlalchemy model в pydantic model
    else:
        raise HTTPException(status_code=500, detail="Не удалось создать ссылку и получить ее ID")


@router.get("/", response_model=List[ImportantLinkInfo])
async def get_all_important_links():
    """
    Возвращает список всех важных ссылок.
    """
    all_links = await repo_links.get_all_links()
    return [ImportantLinkInfo.from_orm(link) for link in
            all_links]  # используем from_orm для преобразования sqlalchemy model в pydantic model


@router.get("/{link_id}", response_model=ImportantLinkInfo)
async def get_important_link_by_id(link_id: int):
    """
    Возвращает важную ссылку по ID.
    """
    important_link = await repo_links.get_link_by_id(link_id)
    if not important_link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    return ImportantLinkInfo.from_orm(
        important_link)  # используем from_orm для преобразования sqlalchemy model в pydantic model


@router.put("/{link_id}", response_model=ImportantLinkInfo)
async def update_important_link(link_id: int, link_update: ImportantLinkUpdate):
    """
    Обновляет существующую важную ссылку.
    """
    updated_link = await repo_links.update_link(
        link_id=link_id,
        link=link_update.link,
        link_text=link_update.link_text,
        icon=link_update.icon
    )
    if not updated_link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    return ImportantLinkInfo.from_orm(
        updated_link)  # используем from_orm для преобразования sqlalchemy model в pydantic model


@router.delete("/{link_id}", status_code=204)
async def delete_important_link(link_id: int):
    """
    Удаляет важную ссылку по ID.
    """
    deleted = await repo_links.delete_link(link_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    return  # 204 No Content - успешное удаление, нет тела ответа
