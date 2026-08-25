from pydantic import BaseModel
from typing import Optional


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: PushSubscriptionKeys
    notify_hours_before: int = 24


class PushSubscriptionOut(BaseModel):
    id: int
    endpoint: str
    notify_hours_before: int
    is_active: bool

    class Config:
        from_attributes = True


class VapidPublicKeyResponse(BaseModel):
    public_key: str
