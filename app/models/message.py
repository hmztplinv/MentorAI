from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    
    # Message data
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    is_voice = Column(Boolean, default=False)  # Whether this message was input via voice
    
    # Sentiment analysis (optional, can be filled by backend)
    sentiment = Column(String)  # e.g., 'positive', 'neutral', 'negative'
    emotion = Column(String)  # e.g., 'happy', 'sad', 'angry', etc.
    
    # Safety flags
    crisis_detected = Column(Boolean, default=False)  # If crisis keywords were detected
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="messages")