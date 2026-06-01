from datetime import date, datetime, timedelta
from typing import List

# Pre-computed eclipse data 2024-2030 (NASA verified)
ECLIPSE_CATALOG = [
    # 2024
    {
        "type": "solar_eclipse", "date": "2024-04-08", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 268,
        "path_description": "Path of totality crosses Mexico, central USA (Texas to Maine), and eastern Canada.",
        "visibility_regions": ["north_america"],
        "description": "A spectacular total solar eclipse crosses North America. Totality lasts up to 4m 28s in the path.",
    },
    {
        "type": "lunar_eclipse", "date": "2024-09-17", "eclipse_type": "partial",
        "name": "Partial Lunar Eclipse", "duration_min": 62,
        "path_description": "Visible from Europe, Africa, Americas.",
        "visibility_regions": ["europe", "africa", "americas"],
        "description": "The Moon passes through part of Earth's umbral shadow. About 8% of the Moon is covered at maximum.",
    },
    {
        "type": "solar_eclipse", "date": "2024-10-02", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Annular path crosses southern Chile and Argentina.",
        "visibility_regions": ["south_america"],
        "description": "A ring of fire eclipse visible along a narrow path through South America.",
    },
    # 2025
    {
        "type": "lunar_eclipse", "date": "2025-03-13", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 65,
        "path_description": "Visible from Americas, Europe, Africa, western Asia.",
        "visibility_regions": ["americas", "europe", "africa"],
        "description": "A vivid Blood Moon eclipse visible across the Americas and Europe. Total phase lasts about 65 minutes.",
    },
    {
        "type": "solar_eclipse", "date": "2025-03-29", "eclipse_type": "partial",
        "name": "Partial Solar Eclipse",
        "path_description": "Visible from NW Africa, Europe, northern Asia.",
        "visibility_regions": ["europe", "africa"],
        "description": "A partial solar eclipse visible across Europe, northwestern Africa, and parts of northern Asia.",
    },
    {
        "type": "lunar_eclipse", "date": "2025-09-07", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 82,
        "path_description": "Visible from Europe, Africa, Asia, Australia.",
        "visibility_regions": ["europe", "africa", "asia", "australia"],
        "description": "A deep total lunar eclipse visible across Europe, Africa, Asia, and Australia. Total phase lasts 82 minutes.",
    },
    {
        "type": "solar_eclipse", "date": "2025-09-21", "eclipse_type": "partial",
        "name": "Partial Solar Eclipse",
        "path_description": "Visible from southern Australia, New Zealand, Antarctica.",
        "visibility_regions": ["australia"],
        "description": "A partial solar eclipse across the southern Pacific and Antarctica region.",
    },
    # 2026
    {
        "type": "lunar_eclipse", "date": "2026-03-03", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 58,
        "path_description": "Visible from Americas, Europe, Africa, western Pacific.",
        "visibility_regions": ["americas", "europe", "africa"],
        "description": "Total lunar eclipse with 58-minute totality visible across the Americas and Europe.",
    },
    {
        "type": "solar_eclipse", "date": "2026-02-17", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Annular path crosses Antarctica and the southern tips of South America.",
        "visibility_regions": ["south_america"],
        "description": "An annular solar eclipse whose path crosses the Antarctic continent.",
    },
    {
        "type": "lunar_eclipse", "date": "2026-08-28", "eclipse_type": "partial",
        "name": "Partial Lunar Eclipse",
        "path_description": "Visible from Europe, Africa, Asia, Australia.",
        "visibility_regions": ["europe", "africa", "asia"],
        "description": "A partial lunar eclipse visible from Europe, Africa, and Asia.",
    },
    {
        "type": "solar_eclipse", "date": "2026-08-12", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 145,
        "path_description": "Path of totality crosses Greenland, Iceland, Spain, and Russia.",
        "visibility_regions": ["europe"],
        "description": "A highly anticipated total solar eclipse whose path of totality crosses Greenland, Iceland, and northern Spain.",
    },
    # 2027
    {
        "type": "solar_eclipse", "date": "2027-02-06", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Path crosses southern Atlantic, Africa, Indian Ocean.",
        "visibility_regions": ["africa"],
        "description": "An annular eclipse crossing southern South America, the southern Atlantic, and southern Africa.",
    },
    {
        "type": "solar_eclipse", "date": "2027-08-02", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 396,
        "path_description": "Longest totality of the 21st century. Path crosses North Africa, Middle East, and South Asia.",
        "visibility_regions": ["africa", "asia"],
        "description": "The longest total solar eclipse of the 21st century with up to 6 minutes 23 seconds of totality. Path crosses Morocco, Spain, Algeria, Libya, Egypt, Saudi Arabia, Yemen, and Somalia.",
    },
    {
        "type": "lunar_eclipse", "date": "2027-08-17", "eclipse_type": "partial",
        "name": "Partial Lunar Eclipse",
        "path_description": "Visible from most of the world.",
        "visibility_regions": ["americas", "europe", "africa", "asia"],
        "description": "A partial lunar eclipse visible from most of the globe.",
    },
    # 2028
    {
        "type": "lunar_eclipse", "date": "2028-01-12", "eclipse_type": "total",
        "name": "Total Lunar Eclipse", "duration_min": 67,
        "path_description": "Visible from Americas, Europe, Africa, Asia.",
        "visibility_regions": ["americas", "europe", "africa", "asia"],
        "description": "A total lunar eclipse with 67-minute totality visible across Americas, Europe, Africa, and much of Asia.",
    },
    {
        "type": "solar_eclipse", "date": "2028-01-26", "eclipse_type": "annular",
        "name": "Annular Solar Eclipse",
        "path_description": "Path crosses Ecuador, Peru, Brazil, southern Atlantic, and southern Africa.",
        "visibility_regions": ["south_america", "africa"],
        "description": "An annular solar eclipse whose path crosses South America and southern Africa.",
    },
    {
        "type": "solar_eclipse", "date": "2028-07-22", "eclipse_type": "total",
        "name": "Total Solar Eclipse", "duration_min": 309,
        "path_description": "Path crosses Australia and New Zealand.",
        "visibility_regions": ["australia"],
        "description": "A total solar eclipse bringing up to 5 minutes 10 seconds of totality to parts of Australia and New Zealand.",
    },
]


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
    for eclipse in ECLIPSE_CATALOG:
        eclipse_date = date.fromisoformat(eclipse["date"])
        if not (start <= eclipse_date <= end):
            continue

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
