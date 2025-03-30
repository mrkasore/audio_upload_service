from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from models.audio_file import AudioFile
from models.user import User
from utils.auth import get_current_user
import aiofiles
import os

router = APIRouter()
MEDIA_DIR = "media"

os.makedirs(MEDIA_DIR, exist_ok=True)

@router.post("/upload", tags=['Аудио, Пользователь'])
async def upload_audio(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith((".mp3", ".wav", ".ogg")):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    ext = file.filename.split(".")[-1]
    new_filename = f"{name}.{ext}"
    full_path = os.path.join(MEDIA_DIR, new_filename)

    async with aiofiles.open(full_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    audio = AudioFile(filename=name, path=full_path, owner_id=current_user.id)
    db.add(audio)
    await db.commit()

    return {"message": "Файл загружен", "filename": name, "path": full_path}

async def get_user_audio_files(user_id: int, db: AsyncSession):
    stmt = select(AudioFile).where(AudioFile.owner_id == user_id)
    result = await db.execute(stmt)
    audio_files = result.scalars().all()
    return [
        {"id": audio.id, "filename": audio.filename, "path": audio.path}
        for audio in audio_files
    ]

@router.get("/my", tags=['Аудио, Пользователь'])
async def get_my_audio_files(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_audio_files(current_user.id, db)

@router.get("/{user_id}", tags=['Аудио, Пользователь'])
async def get_audio_files(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_audio_files(user_id, db)