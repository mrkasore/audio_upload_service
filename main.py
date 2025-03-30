import uvicorn
import asyncio
from fastapi import FastAPI
from routers import auth, users, audio
from database.init_db import on_startup
from utils.openapi import custom_openapi

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(audio.router, prefix="/audio")
app.openapi = lambda: custom_openapi(app)

async def main():
    await on_startup()

if __name__ == '__main__':
    asyncio.run(main())
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)