import json

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from functions.get_current_user import get_current_user
from models import Entry, User
from routes.analyze import analyze_text
from schemas import EntryCreate, EntryResponse, EntrySelectEmotion
from fastapi import Request
from sqlalchemy.future import select

router = APIRouter()


@router.post("/create_entry", response_model=EntryResponse)
async def create_entry(entry: EntryCreate, db: AsyncSession = Depends(get_db)):
    emotions = await analyze_text(entry.text)

    db_entry = Entry(
        title=entry.title,
        text=entry.text,
        user_id=entry.user_id,
        top_emotions=emotions
    )

    async with db.begin():
        db.add(db_entry)
        await db.flush()

    return db_entry



@router.post("/entries/{entry_id}/select-emotion", response_model=EntryResponse)
async def select_emotion(entry_id: int, emotion_data: EntrySelectEmotion, db: AsyncSession = Depends(get_db)):
    valid_emotions = [  'восхищение', 'веселье', 'злость', 'раздражение', 'одобрение', 'забота',
                        'непонимание', 'любопытство', 'желание', 'разочарование', 'неодобрение',
                        'отвращение', 'смущение', 'возбуждение', 'страх', 'признательность', 'горе',
                        'радость', 'любовь', 'нервозность', 'оптимизм', 'гордость', 'осознание',
                        'облегчение', 'раскаяние', 'грусть', 'удивление', 'нейтральность']
    if emotion_data.selected_emotion not in valid_emotions:
        raise HTTPException(status_code=400, detail="Невалидная эмоция")

    async with db.begin():
        result = await db.execute(select(Entry).filter(Entry.id == entry_id))
        db_entry = result.scalar_one_or_none()

    if not db_entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    db_entry.selected_emotion = emotion_data.selected_emotion
    await db.commit()

    return db_entry


@router.get("/entries/{entry_id}", response_model=EntryResponse)
async def get_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Entry).where(Entry.id == entry_id))
        entry = result.scalar_one_or_none()

        if entry is None:
            raise HTTPException(status_code=404, detail="Запись не найдена")

        return entry

@router.get("/entries", response_model=list[EntryResponse])
async def get_user_entries(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    async with db as session:
        result = await session.execute(
            select(Entry).where(Entry.user_id == user.id).order_by(desc(Entry.id))
        )

        entries = result.scalars().all()

        if not entries:
            raise HTTPException(status_code=404, detail="Записей нет")

        return [EntryResponse(
            id=entry.id,
            title=entry.title,
            text=entry.text,
            top_emotions=entry.top_emotions,
            selected_emotion=entry.selected_emotion,
            created_at=entry.created_at
        ) for entry in entries]



