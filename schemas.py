from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


class EntryCreate(BaseModel):
    title: str
    text: str
    user_id: int

class EntryResponse(BaseModel):
    id: int
    title: str
    text: str
    top_emotions: List[dict]
    selected_emotion: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True



class EntrySelectEmotion(BaseModel):
    selected_emotion: str