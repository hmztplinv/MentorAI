from sqlalchemy.orm import Session
from typing import List, Optional, Union

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: Optional[int] = None, username: Optional[str] = None) -> Optional[User]:
    """
    Get user by ID or username
    """
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    if username:
        return db.query(User).filter(User.username == username).first()
    return None


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Get all users with pagination
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user
    """
    db_user = User(
        username=user.username,
        language=user.language,
        preferred_therapy_approach=user.preferred_therapy_approach,
        voice_enabled=user.voice_enabled,
        dark_mode=user.dark_mode
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """
    Update existing user
    """
    db_user = get_user(db, user_id=user_id)
    
    # Update only provided fields
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> User:
    """
    Delete user and return deleted user data
    """
    db_user = get_user(db, user_id=user_id)
    db.delete(db_user)
    db.commit()
    return db_user