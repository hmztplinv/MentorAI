from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    is_voice: Optional[bool] = False


class MessageCreate(MessageBase):
    session_id: int


class MessageUpdate(BaseModel):
    sentiment: Optional[str] = None
    emotion: Optional[str] = None
    crisis_detected: Optional[bool] = None


class MessageInDBBase(MessageBase):
    id: int
    session_id: int
    sentiment: Optional[str] = None
    emotion: Optional[str] = None
    crisis_detected: Optional[bool] = False
    created_at: datetime

    class Config:
        orm_mode = True


class Message(MessageInDBBase):
    pass


class ChatRequest(BaseModel):
    session_id: int
    message: str
    is_voice: Optional[bool] = False


class ChatResponse(BaseModel):
    response: str
    transcribed_text: Optional[str] = None
    crisis_detected: bool = False
    emergency_info: Optional[dict] = None