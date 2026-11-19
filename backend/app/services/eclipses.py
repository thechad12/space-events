"""
Eclipse events, read from the Postgres `eclipses` table (models/eclipse.py).

Seed / resync the table with:  python -m app.seed_eclipses
"""
import logging
from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import select

from ..database import SessionLocal
from ..eclipse_seed_data import ECLIPSE_CATALOG as _SEED_CATALOG
from ..models.eclipse import Eclipse

logger = logging.getLogger(__name__)


def _seed_fallback(start: date, end: date) -> List[dict]:
    return [e for e in _SEED_CATALOG if start <= date.fromisoformat(e["date"]) <= end]


def _load_eclipses(start: date, end: date) -> List[dict]:
    """Eclipses between start and end (inclusive), as plain dicts.

    Falls back to the bundled seed data if the table hasn't been seeded yet or
    the query fails, so the events feed never breaks because of it.
    """
    try:
        with SessionLocal() as db:
            if db.scalar(select(Eclipse.id).limit(1)) is None:
                logger.warning("'eclipses' table is empty — run `python -m app.seed_eclipses`. Serving bundled seed data.")
                return _seed_fallback(start, end)
            rows = db.scalars(
                select(Eclipse).where(Eclipse.date.between(start, end)).order_by(Eclipse.date)
            ).all()
            return [r.to_dict() for r in rows]
    except Exception:
        logger.exception("Failed to load eclipses from the database — serving bundled seed data.")
        return _seed_fallback(start, end)


def _get_region_for_coords(lat: float, lng: float) -> str:
    if -30 <= lat <= 75 and -30 <= lng <= 60:
        return "europe" if lat > 30 else "africa"
    if -60 <= lat <= 75 and -170 <= lng <= -30:
        return "south_america" if lat < 15 else "north_america"
    if lat < -15 and 110 <= lng <= 180:
        return "australia"
    if 10 <= lat <= 80 and 40 <= lng <= 180:
        return "asia"
    return "other"


def _visibility_for_eclipse(eclipse: dict, lat: float, lng: float) -> dict:
    region = _get_region_for_coords(lat, lng)
    in_region = region in eclipse.get("visibility_regions", [])
    eclipse_type = eclipse["eclipse_type"]
    etype = eclipse["type"]

    if etype == "lunar_eclipse":
        if in_region:
            quality = "excellent" if eclipse_type == "total" else "good"
            notes = f"{eclipse_type.title()} lunar eclipse visible from your region. No special equipment needed — visible to the naked eye."
        else:
            quality = "poor"
            notes = "This lunar eclipse is not visible from your location (below the horizon during eclipse)."
    else:  # solar
        if in_region:
            quality = "good"
            notes = f"{eclipse_type.title()} solar eclipse. {'Partial visibility expected at your location.' if eclipse_type != 'total' else 'Check if your location falls in the path of totality.'} Always use solar eclipse glasses."
        else:
            quality = "fair" if eclipse_type == "total" else "poor"
            notes = "Only a partial eclipse (if any) is visible from your location. Solar eclipse glasses required."

    return {"visible": quality != "poor", "quality": quality, "notes": notes}


def get_eclipse_events(lat: float, lng: float, start: date, end: date) -> List[dict]:
    events = []
    for eclipse in _load_eclipses(start, end):
        eclipse_date = date.fromisoformat(eclipse["date"])
        dt = datetime.combine(eclipse_date, datetime.min.time())
        visibility = _visibility_for_eclipse(eclipse, lat, lng)

        events.append({
            "id": f"eclipse_{eclipse['type']}_{eclipse['date']}",
            "type": eclipse["type"],
            "name": eclipse["name"],
            "description": eclipse["description"],
            "start_date": dt.isoformat(),
            "end_date": (dt + timedelta(hours=3)).isoformat(),
            "peak_date": dt.isoformat(),
            "visibility": visibility,
            "details": {
                "eclipse_type": eclipse["eclipse_type"],
                "path_description": eclipse.get("path_description", ""),
                "duration_min": eclipse.get("duration_min"),
            },
        })

    return events
