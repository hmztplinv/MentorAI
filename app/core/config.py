import os
from pydantic import BaseModel
from typing import Dict, List, Optional

class Settings(BaseModel):
    """Application settings"""
    PROJECT_NAME: str = "AI Psychologist"
    API_V1_STR: str = "/api/v1"
    
    # Database
    SQLITE_DB_PATH: str = "sqlite:///./app.db"
    
    # Vector DB (Chroma)
    CHROMA_DB_DIR: str = "./chroma_db"
    
    # Available languages
    LANGUAGES: List[str] = ["en", "tr"]
    DEFAULT_LANGUAGE: str = "tr"
    
    # AI Model settings
    MODEL_NAME: str = "phi4:latest"
    OLLAMA_API_BASE: str = "http://localhost:11434/api"
    
    # Whisper settings
    WHISPER_MODEL: str = "base"
    
    # Memory settings
    SHORT_TERM_MEMORY_LENGTH: int = 10  # Number of messages to keep in conversation
    SUMMARY_THRESHOLD: int = 20  # When to create a summary
    
    # Therapy approaches
    THERAPY_APPROACHES: List[str] = [
        "cbt",           # Cognitive Behavioral Therapy
        "psychoanalytic",
        "humanistic",
        "existential",
        "gestalt",
        "act",           # Acceptance and Commitment Therapy
        "positive",
        "schema",
        "solution_focused",
        "narrative",
        "family_systems",
        "dbt"            # Dialectical Behavior Therapy
    ]
    DEFAULT_APPROACH: str = "cbt"
    
    # Safety settings
    CRISIS_KEYWORDS: List[str] = [
        "suicide", "kill myself", "harm myself", "end my life",
        "intihar", "kendimi öldürmek", "canıma kıymak"
    ]
    
    # Emergency contact info (should be configured by user)
    EMERGENCY_CONTACTS: Dict[str, str] = {
        "tr": {
            "suicide_hotline": "182",
            "emergency": "112",
        },
        "en": {
            "suicide_hotline": "988",
            "emergency": "911",
        }
    }
    
    class Config:
        case_sensitive = True

settings = Settings()