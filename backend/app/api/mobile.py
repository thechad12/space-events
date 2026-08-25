from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.fcm_token import FcmToken
from .deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["mobile"])


class MobileSubscribeRequest(BaseModel):
    fcm_token: str
    platform: str = "ios"


@router.post("/mobile-subscribe", status_code=status.HTTP_204_NO_CONTENT)
def mobile_subscribe(
    payload: MobileSubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(FcmToken).filter(FcmToken.token == payload.fcm_token).first()
    if existing:
        existing.user_id = current_user.id
        existing.is_active = True
    else:
        db.add(FcmToken(
            user_id=current_user.id,
            token=payload.fcm_token,
            platform=payload.platform,
        ))
    db.commit()


@router.delete("/mobile-unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
def mobile_unsubscribe(
    fcm_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(FcmToken).filter(
        FcmToken.token == fcm_token,
        FcmToken.user_id == current_user.id,
    ).update({"is_active": False})
    db.commit()
