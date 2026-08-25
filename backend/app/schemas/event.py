from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    METEOR_SHOWER = "meteor_shower"
    LUNAR_ECLIPSE = "lunar_eclipse"
    SOLAR_ECLIPSE = "solar_eclipse"
    AURORA = "aurora"
    PLANETARY = "planetary"
    COMET = "comet"
    ROCKET_LAUNCH = "rocket_launch"


class VisibilityInfo(BaseModel):
    visible: bool
    quality: str  # excellent, good, fair, poor
    notes: str


class CosmicEvent(BaseModel):
    id: str
    type: EventType
    name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime] = None
    peak_date: Optional[datetime] = None
    visibility: VisibilityInfo
    details: Dict[str, Any] = {}
    image_url: Optional[str] = None


class EventsResponse(BaseModel):
    events: List[CosmicEvent]
    location_name: str
    lat: float
    lng: float
    cached: bool = False
