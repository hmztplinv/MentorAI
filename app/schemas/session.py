from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.message import Message


class SessionBase(BaseModel):
    therapy_approach: str
    title: Optional[str] = None


class SessionCreate(SessionBase):
    user_id: int


class SessionUpdate(BaseModel):
    therapy_approach: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    ended_at: Optional[datetime] = None


class SessionInDBBase(SessionBase):
    id: int
    user_id: int
    summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Session(SessionInDBBase):
    pass


class SessionWithMessages(SessionInDBBase):
    messages: List[Message] = []