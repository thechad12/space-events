"""
Orchestrates all astronomical event sources and handles caching.
"""
import json
from datetime import date, datetime, timedelta
from typing import List, Optional

from ..cache import cache_get, cache_set
from .meteor import get_meteor_shower_events
from .eclipses import get_eclipse_events
from .aurora import get_aurora_events
from .planets import get_planetary_events


def _cache_key(lat: float, lng: float, start: date, end: date) -> str:
    # Round to 1 decimal place so nearby coords share cache
    return f"events:{round(lat,1)}:{round(lng,1)}:{start.isoformat()}:{end.isoformat()}"


async def get_events_for_location(
    lat: float,
    lng: float,
    start: Optional[date] = None,
    end: Optional[date] = None,
    event_types: Optional[List[str]] = None,
) -> List[dict]:
    if start is None:
        start = date.today()
    if end is None:
        end = start + timedelta(days=90)

    key = _cache_key(lat, lng, start, end)
    cached = cache_get(key)
    if cached is not None:
        events = cached
    else:
        meteor_events = get_meteor_shower_events(lat, lng, start, end)
        eclipse_events = get_eclipse_events(lat, lng, start, end)
        aurora_events = await get_aurora_events(lat, lng)
        planetary_events = get_planetary_events(lat, lng, start, end)

        # Aurora events are forecast-based (3 days); filter to requested range
        aurora_filtered = [
            e for e in aurora_events
            if datetime.fromisoformat(e["start_date"]).date() <= end
        ]

        events = meteor_events + eclipse_events + aurora_filtered + planetary_events
        events.sort(key=lambda e: e["start_date"])

        # Cache planetary and eclipse data for 6h; aurora has short TTL baked in via separate key
        cache_set(key, events, ttl=3600 * 6)

    if event_types:
        events = [e for e in events if e["type"] in event_types]

    return events
