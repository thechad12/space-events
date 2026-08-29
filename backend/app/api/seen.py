from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Set

from ..database import get_db
from ..models.seen_event import SeenEvent
from ..models.user import User
from .deps import get_current_user

router = APIRouter(prefix="/seen", tags=["seen"])


class SeenIn(BaseModel):
    event_ids: List[str]


@router.get("", response_model=List[str])
def get_seen_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(SeenEvent.event_id)
        .filter(SeenEvent.user_id == current_user.id)
        .all()
    )
    return [r.event_id for r in rows]


@router.post("", status_code=204)
def mark_seen(
    payload: SeenIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing: Set[str] = {
        r.event_id
        for r in db.query(SeenEvent.event_id)
        .filter(
            SeenEvent.user_id == current_user.id,
            SeenEvent.event_id.in_(payload.event_ids),
        )
        .all()
    }
    new_rows = [
        SeenEvent(user_id=current_user.id, event_id=eid)
        for eid in payload.event_ids
        if eid not in existing
    ]
    if new_rows:
        db.bulk_save_objects(new_rows)
        db.commit()
