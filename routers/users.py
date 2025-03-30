from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from utils.auth import get_current_user, require_superuser
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

router = APIRouter()

@router.get("/me", tags=["Аккаунт, Пользователь"])
async def read_own_profile(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "login": current_user.login, "name": current_user.name}

@router.patch("/me", tags=["Аккаунт, Пользователь"])
async def update_own_profile(name: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = update(User).where(User.id == current_user.id).values(name=name).execution_options(synchronize_session="fetch")
    await db.execute(stmt)
    await db.commit()
    return {"message": "Профиль обновлён", "new_name": name}

@router.delete("/me", tags=["Аккаунт, Пользователь"])
async def delete_own_account(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await db.delete(current_user)
    await db.commit()
    return {"message": "Пользователь удалён"}

@router.get("/{user_id}", tags=["Аккаунт, Пользователь"])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "login": user.login, "name": user.name, "is_superuser": user.is_superuser}

@router.patch("/{user_id}", tags=["Аккаунт, Суперпользователь"])
async def update_user(user_id: int, name: str, db: AsyncSession = Depends(get_db), _: User = Depends(require_superuser)):
    stmt = update(User).where(User.id == user_id).values(name=name).execution_options(synchronize_session="fetch")
    await db.execute(stmt)
    await db.commit()
    return {"message": "Пользователь обновлён", "new_name": name}

@router.delete("/{user_id}", tags=["Аккаунт, Суперпользователь"])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_superuser)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "Пользователь удалён"}


