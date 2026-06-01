from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import date
from ..services.astronomy import get_events_for_location
from ..schemas.event import EventsResponse
from ..models.user import User
from .deps import get_current_user

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventsResponse)
async def get_events(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    location_name: str = Query("Custom Location"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    event_types: Optional[str] = Query(None, description="Comma-separated: meteor_shower,lunar_eclipse,solar_eclipse,aurora,planetary,comet"),
    current_user: User = Depends(get_current_user),
):
    types_filter = [t.strip() for t in event_types.split(",")] if event_types else None
    events = await get_events_for_location(lat, lng, start_date, end_date, types_filter)
    return EventsResponse(
        events=events,
        location_name=location_name,
        lat=lat,
        lng=lng,
    )
