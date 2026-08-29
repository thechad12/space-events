"""
Orchestrates all astronomical event sources and handles caching.
"""
import random
from datetime import date, datetime, timedelta
from typing import List, Optional

from ..cache import cache_get, cache_set, get_redis
from .meteor import get_meteor_shower_events
from .eclipses import get_eclipse_events
from .aurora import get_aurora_events
from .planets import get_planetary_events
from .launches import get_launch_events

CACHE_TTL = 1800          # 30 minutes
EARLY_REFRESH_WINDOW = 300  # start probabilistic refresh in the last 5 min of TTL


def _cache_key(lat: float, lng: float, start: date, end: date) -> str:
    return f"events:{round(lat,1)}:{round(lng,1)}:{start.isoformat()}:{end.isoformat()}"


def _needs_refresh(key: str) -> bool:
    """
    Return True if the cache entry is missing or should be proactively refreshed.
    Within the last EARLY_REFRESH_WINDOW seconds of TTL, probability of refresh
    rises linearly from 0 → 1, so one request naturally takes the refresh hit
    before the cache goes cold for everyone.
    """
    try:
        ttl = get_redis().ttl(key)
    except Exception:
        return True  # Redis unreachable — treat as miss

    if ttl < 0:
        return True  # key missing or no expiry set

    if ttl >= EARLY_REFRESH_WINDOW:
        return False  # plenty of time left, serve from cache

    # Linear probability: 0% at EARLY_REFRESH_WINDOW seconds remaining → 100% at 0
    refresh_prob = 1.0 - (ttl / EARLY_REFRESH_WINDOW)
    return random.random() < refresh_prob


async def _fetch_and_cache(key: str, lat: float, lng: float, start: date, end: date) -> List[dict]:
    meteor_events = get_meteor_shower_events(lat, lng, start, end)
    eclipse_events = get_eclipse_events(lat, lng, start, end)
    aurora_events = await get_aurora_events(lat, lng)
    planetary_events = get_planetary_events(lat, lng, start, end)
    launch_events = await get_launch_events(lat, lng, start, end)

    aurora_filtered = [
        e for e in aurora_events
        if datetime.fromisoformat(e["start_date"]).date() <= end
    ]

    events = meteor_events + eclipse_events + aurora_filtered + planetary_events + launch_events
    events.sort(key=lambda e: e["start_date"])
    cache_set(key, events, ttl=CACHE_TTL)
    return events


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

    if _needs_refresh(key):
        events = await _fetch_and_cache(key, lat, lng, start, end)
    else:
        events = cache_get(key) or await _fetch_and_cache(key, lat, lng, start, end)

    if event_types:
        events = [e for e in events if e["type"] in event_types]

    return events
