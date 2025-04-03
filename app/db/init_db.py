import os
import chromadb
from app.db.base import Base, engine
from app.core.config import settings

# Import all models to create tables
from app.models.user import User
from app.models.session import Session
from app.models.message import Message

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

def init_vector_db():
    """Initialize Chroma vector database"""
    # Create directory if it doesn't exist
    os.makedirs(settings.chromadb_DIR, exist_ok=True)
    
    # Initialize Chroma client
    client = chromadb.PersistentClient(path=settings.chromadb_DIR)
    
    # Create collections for long-term memory if they don't exist
    try:
        client.get_collection("user_memories")
    except:
        client.create_collection("user_memories")
    
    print("Vector database initialized")

def init_db():
    """Initialize both databases"""
    create_tables()
    init_vector_db()
    print("All databases initialized successfully")

if __name__ == "__main__":
    init_db()