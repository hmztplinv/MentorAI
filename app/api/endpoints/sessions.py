from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import get_user, get_users, create_user, update_user, delete_user

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=User)
def create_new_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db)
):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=User)
def update_user_data(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db)
):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_user(db=db, user_id=user_id, user_data=user_data)
    return updated_user


@router.delete("/{user_id}", response_model=User)
def delete_user_data(
    user_id: int, 
    db: Session = Depends(get_db)
):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = delete_user(db=db, user_id=user_id)
    return deleted_user