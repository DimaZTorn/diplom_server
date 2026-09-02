from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User, hash_password, verify_password
from schemas import UserCreate, UserLogin
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User).where(User.username == user.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")

        new_user = User(
            username=user.username,
            email=user.email,
            password_hash=hash_password(user.password)
        )
        session.add(new_user)
        await session.commit()
        return {"message": "Регистрация успешна!"}

import logging

logging.basicConfig(level=logging.INFO)

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(User).where(User.username == user.username))
        existing_user = result.scalars().first()

        logging.info(f"Existing user: {existing_user.__dict__}")

        if not existing_user or not verify_password(user.password, existing_user.password_hash):
            raise HTTPException(status_code=401, detail="Неверные учетные данные")

        token = create_access_token({"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        logging.info(f"Token: {token}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": existing_user.id
        }



