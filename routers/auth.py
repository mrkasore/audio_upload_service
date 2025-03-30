from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from utils.auth import get_yandex_access_token, get_yandex_user_info, create_internal_token
from models.user import get_or_create_user
import os

router = APIRouter()

YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
REDIRECT_URI = "/auth/callback"

@router.get("/login")
async def login():
    return RedirectResponse(
        f"{YANDEX_AUTH_URL}?response_type=code&client_id={os.getenv('YANDEX_CLIENT_ID')}&redirect_uri={os.getenv('BASE_URL')}{REDIRECT_URI}"
    )

@router.get("/callback")
async def callback(code: str, db: AsyncSession = Depends(get_db)):
    try:
        token_data = await get_yandex_access_token(code)
        user_info = await get_yandex_user_info(token_data['access_token'])
        user = await get_or_create_user(db, user_info)
        internal_token = create_internal_token(user.id)

        return {"access_token": internal_token, "token_type": "bearer"}
    except Exception as e:
        print("Callback error:", e)
        raise HTTPException(status_code=500, detail=str(e))