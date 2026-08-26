import httpx
from datetime import datetime, timedelta, timezone
from typing import List, Optional

NOAA_KP_FORECAST_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
NOAA_3DAY_URL = "https://services.swpc.noaa.gov/json/3-day-forecast.json"


def _min_kp_for_latitude(lat: float) -> float:
    abs_lat = abs(lat)
    if abs_lat >= 70:
        return 1.0
    if abs_lat >= 65:
        return 2.0
    if abs_lat >= 60:
        return 3.0
    if abs_lat >= 55:
        return 4.0
    if abs_lat >= 50:
        return 5.0
    if abs_lat >= 45:
        return 6.0
    if abs_lat >= 40:
        return 7.0
    if abs_lat >= 35:
        return 8.0
    return 9.5  # effectively not visible at low latitudes


def _quality_from_kp(kp: float, min_kp: float) -> str:
    margin = kp - min_kp
    if margin >= 2:
        return "excellent"
    if margin >= 1:
        return "good"
    if margin >= 0:
        return "fair"
    return "poor"


async def get_aurora_events(lat: float, lng: float) -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(NOAA_KP_FORECAST_URL)
            if resp.status_code != 200:
                return []
            raw = resp.json()
    except Exception:
        return []

    min_kp = _min_kp_for_latitude(lat)
    events = []
    aurora_windows = []
    current_window = None

    for row in raw:
        try:
            # API returns dicts: {time_tag, kp, observed, noaa_scale}
            time_str = row["time_tag"] if isinstance(row, dict) else row[0]
            kp = float(row["kp"] if isinstance(row, dict) else row[1])
            dt = datetime.fromisoformat(time_str.replace(" ", "T")).replace(tzinfo=timezone.utc)
        except (ValueError, KeyError, IndexError, TypeError):
            continue

        if kp >= min_kp:
            if current_window is None:
                current_window = {"start": dt, "end": dt, "max_kp": kp}
            else:
                current_window["end"] = dt
                current_window["max_kp"] = max(current_window["max_kp"], kp)
        else:
            if current_window:
                aurora_windows.append(current_window)
                current_window = None

    if current_window:
        aurora_windows.append(current_window)

    for i, window in enumerate(aurora_windows):
        max_kp = window["max_kp"]
        quality = _quality_from_kp(max_kp, min_kp)
        hemisphere = "Northern" if lat >= 0 else "Southern"
        kp_label = _kp_storm_label(max_kp)

        events.append({
            "id": f"aurora_{window['start'].strftime('%Y%m%d%H')}_{i}",
            "type": "aurora",
            "name": f"Aurora {hemisphere} Lights — {kp_label}",
            "description": (
                f"A geomagnetic storm (Kp={max_kp:.1f}) may produce aurora at your latitude. "
                f"Best viewed away from city lights, ideally after midnight local time. "
                f"Look toward the {'north' if lat >= 0 else 'south'}ern horizon."
            ),
            "start_date": window["start"].isoformat(),
            "end_date": (window["end"] + timedelta(hours=3)).isoformat(),
            "peak_date": window["start"].isoformat(),
            "visibility": {
                "visible": True,
                "quality": quality,
                "notes": f"Kp index forecast: {max_kp:.1f}. Minimum Kp needed at your latitude: {min_kp:.1f}.",
            },
            "details": {
                "max_kp": max_kp,
                "min_kp_needed": min_kp,
                "storm_level": kp_label,
                "source": "NOAA Space Weather Prediction Center",
            },
        })

    return events


def _kp_storm_label(kp: float) -> str:
    if kp >= 9:
        return "Extreme (G5)"
    if kp >= 8:
        return "Severe (G4)"
    if kp >= 7:
        return "Strong (G3)"
    if kp >= 6:
        return "Moderate (G2)"
    if kp >= 5:
        return "Minor (G1)"
    return "Active"
