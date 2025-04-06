import asyncio

from fastapi import APIRouter, Response, HTTPException, Depends
from pydantic import BaseModel
from src.api.auth.security import security, config, pwd_context
from src.api.auth.user_repo import user_repository
from src.api.schedule.parsing_utils import auth_check
from src.api.schedule.router import fetch_content_with_ntlm_auth

router = APIRouter(prefix='/auth', tags=["Auth"])


class UserLoginSchema(BaseModel):
    login: str
    password: str


@router.post('/login')
async def login(creds: UserLoginSchema, response: Response):
    user = await user_repository.get_user_by_username(creds.login)
    if not user:
        auth_url = 'https://is.ku.edu.kz/e-Rectorat/Services/Cabinet/Student/Notes.asp'
        is_auth = await fetch_content_with_ntlm_auth(auth_url, creds.login, creds.password)
        if not is_auth:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_data = {
            "login": creds.login,
            "password": creds.password,
            "role": "user",
        }
        user = await user_repository.create_user(user_data)

    if not pwd_context.verify(creds.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    data = {"role": user.role}

    token = security.create_access_token(uid=str(user.id), data=data)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)

    return {'access_token': token}


async def create_admin():
    # hashed_password = pwd_context.hash("333")
    # await user_repository.create_user(username="ё", hashed_password=hashed_password, role="inspector")
    hashed_password = pwd_context.hash("admin")
    await user_repository.create_user(username="admin", hashed_password=hashed_password, role="admin")
    print("Admin user created")


if __name__ == '__main__':
    asyncio.run(create_admin())
