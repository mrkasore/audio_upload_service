from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from utils.auth import get_yandex_access_token, get_yandex_user_info, create_access_token, create_refresh_token
from models.user import User, get_or_create_user
import os
import jwt

router = APIRouter()

YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
REDIRECT_URI = "/auth/callback"

@router.get("/login", tags=['Авторизация'], summary="Ручка работает при ручном переходе по url!")
async def login():
    return RedirectResponse(
        f"{YANDEX_AUTH_URL}?response_type=code&client_id={os.getenv('YANDEX_CLIENT_ID')}&redirect_uri={os.getenv('BASE_URL')}{REDIRECT_URI}"
    )

@router.get("/callback", tags=['Авторизация'])
async def callback(code: str, db: AsyncSession = Depends(get_db)):
    try:
        token_data = await get_yandex_access_token(code)
        user_info = await get_yandex_user_info(token_data['access_token'])
        user = await get_or_create_user(db, user_info)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except Exception as e:
        print("Callback error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", tags=['Авторизация'])
async def refresh_tokens(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id = int(payload.get("sub"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(user_id)
    return {"access_token": new_access_token, "token_type": "bearer"}