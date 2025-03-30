import httpx
import os
import jwt
from datetime import datetime, timedelta

async def get_yandex_access_token(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post("https://oauth.yandex.ru/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": os.getenv("YANDEX_CLIENT_ID"),
            "client_secret": os.getenv("YANDEX_CLIENT_SECRET"),
        })
        response.raise_for_status()
        return response.json()

async def get_yandex_user_info(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://login.yandex.ru/info",
            headers={
                "Authorization": f"OAuth {access_token}"
            },
            params={
                "format": "json"
            }
        )
        response.raise_for_status()
        return response.json()

def create_internal_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))