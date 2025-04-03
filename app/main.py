from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.db.init_db import create_tables

app = FastAPI(
    title="AI Psychologist API",
    description="Backend API for AI Psychologist Application",
    version="0.1.0",
)

# Set up CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    # Create DB tables on startup
    create_tables()

@app.get("/")
async def root():
    return {"message": "AI Psychologist API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)