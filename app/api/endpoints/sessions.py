from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.schemas.session import Session, SessionCreate, SessionUpdate, SessionWithMessages
from app.services.session_service import get_session, get_sessions_by_user, create_session, update_session, end_session, delete_session

router = APIRouter()

@router.get("/", response_model=List[Session])
def read_sessions(
    user_id: int,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    sessions = get_sessions_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return sessions

@router.post("/", response_model=Session)
def create_new_session(
    session: SessionCreate, 
    db: Session = Depends(get_db)
):
    return create_session(db=db, session=session)

@router.get("/{session_id}", response_model=SessionWithMessages)
def read_session(
    session_id: int, 
    db: Session = Depends(get_db)
):
    db_session = get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.put("/{session_id}", response_model=Session)
def update_session_data(
    session_id: int, 
    session_data: SessionUpdate, 
    db: Session = Depends(get_db)
):
    db_session = get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    updated_session = update_session(db=db, session_id=session_id, session_data=session_data)
    return updated_session

@router.put("/{session_id}/end", response_model=Session)
def end_session_route(
    session_id: int,
    db: Session = Depends(get_db)
):
    db_session = get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if db_session.ended_at is not None:
        raise HTTPException(status_code=400, detail="Session already ended")
    ended_session = end_session(db=db, session_id=session_id)
    return ended_session

@router.delete("/{session_id}", response_model=Session)
def delete_session_data(
    session_id: int, 
    db: Session = Depends(get_db)
):
    db_session = get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    deleted_session = delete_session(db=db, session_id=session_id)
    return deleted_session