from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.bookmark import BookmarkedEvent
from ..models.user import User
from .deps import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


class BookmarkIn(BaseModel):
    event_id: str
    event_type: str
    event_name: str
    event_date: str  # ISO string


class BookmarkOut(BaseModel):
    id: int
    event_id: str
    event_type: str
    event_name: str
    event_date: str
    bookmarked_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[BookmarkOut])
def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(BookmarkedEvent)
        .filter(BookmarkedEvent.user_id == current_user.id)
        .order_by(BookmarkedEvent.bookmarked_at.desc())
        .all()
    )


@router.post("", response_model=BookmarkOut, status_code=201)
def add_bookmark(
    payload: BookmarkIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(BookmarkedEvent)
        .filter(
            BookmarkedEvent.user_id == current_user.id,
            BookmarkedEvent.event_id == payload.event_id,
        )
        .first()
    )
    if existing:
        return existing

    bm = BookmarkedEvent(
        user_id=current_user.id,
        event_id=payload.event_id,
        event_type=payload.event_type,
        event_name=payload.event_name,
        event_date=payload.event_date,
    )
    db.add(bm)
    db.commit()
    db.refresh(bm)
    return bm


@router.delete("/{event_id}", status_code=204)
def remove_bookmark(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bm = (
        db.query(BookmarkedEvent)
        .filter(
            BookmarkedEvent.user_id == current_user.id,
            BookmarkedEvent.event_id == event_id,
        )
        .first()
    )
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bm)
    db.commit()
