from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    yandex_id = Column(String, unique=True, index=True)
    login = Column(String)
    name = Column(String)

async def get_or_create_user(db: AsyncSession, user_info: dict):
    stmt = select(User).where(User.yandex_id == user_info['id'])
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        user = User(
            yandex_id=user_info['id'],
            login=user_info.get('login'),
            name=user_info.get('real_name')
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user