from database.session import Base, engine

async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)