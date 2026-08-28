"""
Rocket launch events from The Space Devs Launch Library 2 API.
Visibility uses a trajectory-corridor model so East Coast users see
Cape Canaveral NE launches even at 800+ miles distance.
"""
import httpx
import ephem
from datetime import datetime, date, timedelta, timezone
from math import radians, sin, cos, sqrt, atan2
from typing import List, Optional

from ..cache import cache_get, cache_set

SPACE_DEVS_URL = "https://ll.thespacedevs.com/2.2.0/launches/upcoming/"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _is_dark(user_lat: float, user_lng: float, launch_utc: datetime) -> bool:
    """True if sun is below civil-twilight angle (-6°) at user location at launch time."""
    try:
        obs = ephem.Observer()
        obs.lat = str(user_lat)
        obs.lon = str(user_lng)
        obs.date = ephem.Date(launch_utc)
        sun = ephem.Sun()
        sun.compute(obs)
        return float(sun.alt) * (180 / 3.14159265) < -6.0
    except Exception:
        return False


def _launch_visibility(
    user_lat: float,
    user_lng: float,
    launch_lat: float,
    launch_lng: float,
    orbit_abbrev: str,
    launch_utc: datetime,
) -> dict:
    """
    Compute visibility of a rocket launch from user's location.

    Key insight: rockets bound for NE-inclined orbits (ISS, most Starlink)
    from Florida fly up the East Coast at 150–250 km altitude, where they can
    be seen from 1,000+ km away in the dark. We model this 'corridor' explicitly.
    """
    dist_km = _haversine_km(user_lat, user_lng, launch_lat, launch_lng)
    is_dark = _is_dark(user_lat, user_lng, launch_utc)

    # --- Trajectory corridor detection ---

    # Cape Canaveral / Kennedy Space Center area heading NE
    from_fl = -82 < launch_lng < -78 and 27 < launch_lat < 30
    # Vandenberg SFB heading south/polar
    from_vafb = -121 < launch_lng < -119 and 34 < launch_lat < 35

    ne_orbits = {"ISS", "LEO", "SSO", "VLEO", "MEO"}
    polar_orbits = {"PO", "SSO", "SO", "HEO"}

    # East Coast NE corridor: user north of FL site on the eastern seaboard
    in_ne_corridor = (
        from_fl
        and orbit_abbrev in ne_orbits
        and user_lat > launch_lat       # north of launch site
        and -85 < user_lng < -60        # Eastern North America / Atlantic
        and user_lat < 55
    )

    # California polar corridor (Vandenberg): Pacific coast north/south
    in_polar_corridor = (
        from_vafb
        and orbit_abbrev in polar_orbits
        and abs(user_lat - launch_lat) < 20
        and -130 < user_lng < -115
    )

    in_corridor = in_ne_corridor or in_polar_corridor

    # Max visible distance based on conditions
    if dist_km <= 50:
        quality = "excellent"
        notes = "You'll see the launch pad glow on the horizon. The roar may reach you within minutes."
    elif dist_km <= 150:
        quality = "excellent"
        notes = "Excellent view — the rocket will be a brilliant flame rising steadily into the sky."
    elif dist_km <= 350 and is_dark:
        quality = "excellent"
        notes = "The rocket will appear as a bright moving star, leaving a glowing exhaust plume."
    elif dist_km <= 350:
        quality = "good"
        notes = "Visible in daylight as a bright flame and rising smoke/contrail."
    elif dist_km <= 700 and is_dark and in_corridor:
        quality = "good"
        notes = (
            "The rocket will arc across the sky heading northeast. "
            "Watch for the bright second-stage engine and spreading exhaust cloud."
        )
    elif dist_km <= 700 and is_dark:
        quality = "fair"
        notes = "May be visible on a clear night. Look toward the launch site on the horizon."
    elif dist_km <= 700:
        quality = "fair"
        notes = "Possibly visible as a thin contrail in good conditions."
    elif dist_km <= 1400 and is_dark and in_corridor:
        quality = "fair"
        notes = (
            "The rocket flies high overhead on its NE trajectory. "
            "Watch for a bright moving light and expanding exhaust contrail lit by sunlight "
            "even after local sunset. Look south to southeast."
        )
    else:
        quality = "poor"
        notes = "Too far from the launch site to observe."

    return {
        "visible": quality != "poor",
        "quality": quality,
        "notes": notes,
        "in_corridor": in_corridor,
        "distance_km": round(dist_km),
    }


def _parse_launch(raw: dict, user_lat: float, user_lng: float) -> Optional[dict]:
    try:
        pad = raw.get("pad", {})
        pad_loc = pad.get("location", {})
        launch_lat = float(pad_loc.get("latitude", 0) or 0)
        launch_lng = float(pad_loc.get("longitude", 0) or 0)
        if launch_lat == 0 and launch_lng == 0:
            return None

        net_str = raw.get("net") or raw.get("window_start")
        if not net_str:
            return None
        launch_utc = datetime.fromisoformat(net_str.replace("Z", "+00:00"))

        orbit_abbrev = (raw.get("mission") or {}).get("orbit", {})
        orbit_abbrev = (orbit_abbrev.get("abbrev") if isinstance(orbit_abbrev, dict) else None) or "LEO"

        rocket_name = (raw.get("rocket") or {}).get("configuration", {}).get("full_name", "Unknown Rocket")
        mission_name = (raw.get("mission") or {}).get("name") or raw.get("name", "Unknown Mission")
        mission_desc = (raw.get("mission") or {}).get("description") or ""
        status_name = (raw.get("status") or {}).get("name", "")

        vis = _launch_visibility(user_lat, user_lng, launch_lat, launch_lng, orbit_abbrev, launch_utc)

        dist_km = vis.pop("distance_km")
        in_corridor = vis.pop("in_corridor")

        return {
            "id": f"launch_{raw['id']}",
            "type": "rocket_launch",
            "name": f"{rocket_name} | {mission_name}",
            "description": mission_desc or f"{rocket_name} launches from {pad.get('name', 'unknown pad')}.",
            "start_date": launch_utc.isoformat(),
            "end_date": (launch_utc + timedelta(minutes=15)).isoformat(),
            "peak_date": launch_utc.isoformat(),
            "visibility": vis,
            "image_url": raw.get("image"),
            "details": {
                "rocket": rocket_name,
                "mission": mission_name,
                "orbit": orbit_abbrev,
                "launch_site": pad.get("name", ""),
                "launch_site_location": pad_loc.get("name", ""),
                "status": status_name,
                "distance_km": dist_km,
                "trajectory_corridor": in_corridor,
                "launch_site_lat": launch_lat,
                "launch_site_lng": launch_lng,
                "window_start": raw.get("window_start"),
                "window_end": raw.get("window_end"),
            },
        }
    except Exception:
        return None


async def get_launch_events(user_lat: float, user_lng: float, start: date, end: date) -> List[dict]:
    # Cache raw API response (not per-user; visibility is computed per-user)
    raw_key = "launches:raw"
    raw_cached = cache_get(raw_key)

    if raw_cached is None:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    SPACE_DEVS_URL,
                    params={"limit": 50, "format": "json"},
                    headers={"User-Agent": "LookUp/1.0"},
                )
            if resp.status_code != 200:
                return []
            raw_cached = resp.json().get("results", [])
            cache_set(raw_key, raw_cached, ttl=1800)  # 30-min cache
        except Exception:
            return []

    events = []
    for raw in raw_cached:
        try:
            net_str = raw.get("net") or raw.get("window_start")
            if not net_str:
                continue
            launch_date = datetime.fromisoformat(net_str.replace("Z", "+00:00")).date()
            if not (start <= launch_date <= end):
                continue
        except Exception:
            continue

        event = _parse_launch(raw, user_lat, user_lng)
        if event:
            events.append(event)

    return events
