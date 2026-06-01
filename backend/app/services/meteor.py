from datetime import date, datetime, timedelta
from typing import List
import uuid

METEOR_SHOWERS = [
    {
        "name": "Quadrantids",
        "peak_month": 1, "peak_day": 3,
        "active_days_before": 5, "active_days_after": 5,
        "peak_rate": 120,
        "hemisphere": "north",
        "radiant": "Boötes",
        "description": "One of the strongest annual showers with a very narrow peak window. Best seen from the Northern Hemisphere in the pre-dawn hours.",
    },
    {
        "name": "Lyrids",
        "peak_month": 4, "peak_day": 22,
        "active_days_before": 5, "active_days_after": 3,
        "peak_rate": 18,
        "hemisphere": "both",
        "radiant": "Lyra",
        "description": "One of the oldest recorded meteor showers, with records dating back 2,600 years. Occasional outbursts can produce up to 100 meteors/hour.",
    },
    {
        "name": "Eta Aquariids",
        "peak_month": 5, "peak_day": 6,
        "active_days_before": 10, "active_days_after": 10,
        "peak_rate": 50,
        "hemisphere": "south",
        "radiant": "Aquarius",
        "description": "Debris from Halley's Comet. Best viewed from the Southern Hemisphere, producing fast meteors with persistent trains.",
    },
    {
        "name": "Delta Aquariids",
        "peak_month": 7, "peak_day": 30,
        "active_days_before": 15, "active_days_after": 10,
        "peak_rate": 20,
        "hemisphere": "south",
        "radiant": "Aquarius",
        "description": "A broad, steady shower best seen from the Southern Hemisphere and southern latitudes of the Northern Hemisphere.",
    },
    {
        "name": "Perseids",
        "peak_month": 8, "peak_day": 12,
        "active_days_before": 7, "active_days_after": 5,
        "peak_rate": 100,
        "hemisphere": "north",
        "radiant": "Perseus",
        "description": "The most beloved annual meteor shower. Debris from Comet Swift-Tuttle produces fast, bright meteors, often with fireballs.",
    },
    {
        "name": "Orionids",
        "peak_month": 10, "peak_day": 21,
        "active_days_before": 7, "active_days_after": 7,
        "peak_rate": 20,
        "hemisphere": "both",
        "radiant": "Orion",
        "description": "The second shower produced by Halley's Comet. Notable for fast meteors and persistent trains visible in both hemispheres.",
    },
    {
        "name": "Leonids",
        "peak_month": 11, "peak_day": 17,
        "active_days_before": 5, "active_days_after": 3,
        "peak_rate": 15,
        "hemisphere": "both",
        "radiant": "Leo",
        "description": "Debris from Comet Tempel-Tuttle. While typically modest, Leonids can produce spectacular meteor storms every 33 years.",
    },
    {
        "name": "Geminids",
        "peak_month": 12, "peak_day": 14,
        "active_days_before": 5, "active_days_after": 5,
        "peak_rate": 150,
        "hemisphere": "both",
        "radiant": "Gemini",
        "description": "The king of meteor showers, producing multicolored meteors from asteroid 3200 Phaethon. Active early in the evening.",
    },
    {
        "name": "Ursids",
        "peak_month": 12, "peak_day": 22,
        "active_days_before": 3, "active_days_after": 3,
        "peak_rate": 10,
        "hemisphere": "north",
        "radiant": "Ursa Minor",
        "description": "A modest Northern Hemisphere shower that coincides with the winter solstice, produced by Comet Tuttle.",
    },
]


def get_meteor_shower_events(lat: float, lng: float, start: date, end: date) -> List[dict]:
    events = []
    year = start.year

    for shower in METEOR_SHOWERS:
        for y in [year, year + 1]:
            try:
                peak = date(y, shower["peak_month"], shower["peak_day"])
            except ValueError:
                continue

            active_start = peak - timedelta(days=shower["active_days_before"])
            active_end = peak + timedelta(days=shower["active_days_after"])

            if active_end < start or active_start > end:
                continue

            hemisphere = shower.get("hemisphere", "both")
            if hemisphere == "north" and lat < -20:
                quality = "poor"
                notes = "This shower favors the Northern Hemisphere."
            elif hemisphere == "south" and lat > 20:
                quality = "fair"
                notes = "Best viewed from the Southern Hemisphere; reduced visibility at your latitude."
            else:
                quality = "excellent"
                notes = f"Great viewing conditions at your latitude. Look toward {shower['radiant']} before dawn."

            visible = quality != "poor"

            events.append({
                "id": f"meteor_{shower['name'].lower().replace(' ', '_')}_{y}",
                "type": "meteor_shower",
                "name": f"{shower['name']} Meteor Shower",
                "description": shower["description"],
                "start_date": datetime.combine(active_start, datetime.min.time()).isoformat(),
                "end_date": datetime.combine(active_end, datetime.min.time()).isoformat(),
                "peak_date": datetime.combine(peak, datetime.min.time()).isoformat(),
                "visibility": {"visible": visible, "quality": quality, "notes": notes},
                "details": {
                    "peak_rate": shower["peak_rate"],
                    "radiant": shower["radiant"],
                    "hemisphere": hemisphere,
                },
            })

    return events
