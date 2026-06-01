from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LocationCreate(BaseModel):
    name: str
    lat: float
    lng: float
    timezone: Optional[str] = None
    is_default: bool = False


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    is_default: Optional[bool] = None


class LocationOut(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    timezone: Optional[str]
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GeocodeResult(BaseModel):
    name: str
    lat: float
    lng: float
    display_name: str
