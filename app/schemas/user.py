from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    language: Optional[str] = "tr"
    preferred_therapy_approach: Optional[str] = "cbt"
    voice_enabled: Optional[bool] = False
    dark_mode: Optional[bool] = False


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    language: Optional[str] = None
    preferred_therapy_approach: Optional[str] = None
    voice_enabled: Optional[bool] = None
    dark_mode: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass