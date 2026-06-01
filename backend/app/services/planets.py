"""
Planetary event calculations using ephem.
Covers oppositions, conjunctions with the Sun, and elongation events.
"""
from datetime import date, datetime, timedelta
from typing import List
import ephem


PLANETS = [
    ("Mercury", ephem.Mercury(), "mercury"),
    ("Venus", ephem.Venus(), "venus"),
    ("Mars", ephem.Mars(), "mars"),
    ("Jupiter", ephem.Jupiter(), "jupiter"),
    ("Saturn", ephem.Saturn(), "saturn"),
    ("Uranus", ephem.Uranus(), "uranus"),
    ("Neptune", ephem.Neptune(), "neptune"),
]

OUTER_PLANETS = {"mars", "jupiter", "saturn", "uranus", "neptune"}
INNER_PLANETS = {"mercury", "venus"}


def _elongation_deg(planet_obj, dt: datetime) -> float:
    sun = ephem.Sun()
    sun.compute(ephem.Date(dt))
    planet_obj.compute(ephem.Date(dt))
    return float(ephem.separation(planet_obj, sun)) * (180 / 3.14159265)


def _find_opposition(planet_key: str, planet_obj, start: date, end: date) -> List[dict]:
    events = []
    if planet_key not in OUTER_PLANETS:
        return events

    current = datetime(start.year, start.month, start.day)
    end_dt = datetime(end.year, end.month, end.day)
    step = timedelta(days=1)
    prev_elong = None

    while current <= end_dt:
        elong = _elongation_deg(planet_obj, current)
        if prev_elong is not None:
            # Opposition: elongation crosses 180°
            if prev_elong < 175 and elong >= 175:
                planet_obj.compute(ephem.Date(current))
                mag = planet_obj.mag

                name_map = {
                    "mars": "Mars at Opposition",
                    "jupiter": "Jupiter at Opposition",
                    "saturn": "Saturn at Opposition",
                    "uranus": "Uranus at Opposition",
                    "neptune": "Neptune at Opposition",
                }
                planet_name = planet_key.capitalize()
                desc_map = {
                    "mars": f"Mars is at opposition — closest approach to Earth this year. Mars rises at sunset and is visible all night at magnitude {mag:.1f}. Look for its distinctive reddish hue.",
                    "jupiter": f"Jupiter at its closest and brightest of the year. Visible all night at magnitude {mag:.1f}. A small telescope will reveal the four Galilean moons.",
                    "saturn": f"Saturn at opposition — rings at their most spectacular. Visible all night at magnitude {mag:.1f}. Even a small telescope shows the rings clearly.",
                    "uranus": f"Uranus at opposition, reaching magnitude {mag:.1f}. Binoculars reveal a pale blue-green disc.",
                    "neptune": f"Neptune at opposition at magnitude {mag:.1f}. Requires a telescope to resolve its tiny blue-green disc.",
                }

                events.append({
                    "id": f"planet_{planet_key}_opposition_{current.strftime('%Y%m%d')}",
                    "type": "planetary",
                    "name": name_map.get(planet_key, f"{planet_name} at Opposition"),
                    "description": desc_map.get(planet_key, f"{planet_name} is at opposition and at its closest and brightest."),
                    "start_date": current.isoformat(),
                    "end_date": (current + timedelta(days=3)).isoformat(),
                    "peak_date": current.isoformat(),
                    "visibility": {
                        "visible": True,
                        "quality": "excellent" if planet_key in ("mars", "jupiter", "saturn") else "good",
                        "notes": f"Visible all night. Rises in the east at sunset. Magnitude {mag:.1f}.",
                    },
                    "details": {
                        "planet": planet_name,
                        "event_subtype": "opposition",
                        "magnitude": round(float(mag), 2),
                    },
                })

        prev_elong = elong
        current += step

    return events


def _find_greatest_elongation(planet_key: str, planet_obj, start: date, end: date) -> List[dict]:
    events = []
    if planet_key not in INNER_PLANETS:
        return events

    current = datetime(start.year, start.month, start.day)
    end_dt = datetime(end.year, end.month, end.day)
    step = timedelta(days=1)
    prev_elong = None
    descending = False

    while current <= end_dt:
        elong = _elongation_deg(planet_obj, current)
        if prev_elong is not None:
            if elong < prev_elong and not descending and prev_elong > 10:
                # Local maximum = greatest elongation
                planet_obj.compute(ephem.Date(current))
                mag = float(planet_obj.mag)
                direction = "Evening" if float(planet_obj.az) > 180 else "Morning"

                events.append({
                    "id": f"planet_{planet_key}_elongation_{current.strftime('%Y%m%d')}",
                    "type": "planetary",
                    "name": f"{planet_key.capitalize()} at Greatest Elongation ({direction})",
                    "description": (
                        f"{planet_key.capitalize()} reaches its maximum angular distance from the Sun, "
                        f"making it easiest to observe. Look {direction.lower()} of the Sun "
                        f"({'after sunset' if direction == 'Evening' else 'before sunrise'})."
                    ),
                    "start_date": current.isoformat(),
                    "end_date": (current + timedelta(days=5)).isoformat(),
                    "peak_date": current.isoformat(),
                    "visibility": {
                        "visible": True,
                        "quality": "good",
                        "notes": f"Best time to observe {planet_key.capitalize()} — farthest from Sun's glare. Magnitude {mag:.1f}.",
                    },
                    "details": {
                        "planet": planet_key.capitalize(),
                        "event_subtype": "greatest_elongation",
                        "elongation_deg": round(prev_elong, 1),
                        "magnitude": round(mag, 2),
                        "direction": direction,
                    },
                })
                descending = True
            elif elong > prev_elong:
                descending = False
        prev_elong = elong
        current += step

    return events


def get_planetary_events(lat: float, lng: float, start: date, end: date) -> List[dict]:
    events = []
    for name, obj, key in PLANETS:
        try:
            if key in OUTER_PLANETS:
                events.extend(_find_opposition(key, obj, start, end))
            else:
                events.extend(_find_greatest_elongation(key, obj, start, end))
        except Exception:
            continue
    return events
