from fastapi import APIRouter
from app.api.endpoints import users, sessions, chat, voice

api_router = APIRouter()

# Include all API endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])