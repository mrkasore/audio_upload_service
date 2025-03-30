import httpx
import os
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from database.session import get_db
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

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

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id = int(payload.get("sub"))
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user

async def require_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user