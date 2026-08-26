from datetime import date, datetime, timedelta
from typing import List

METEOR_SHOWERS = [
    {
        "name": "Quadrantids",
        "peak_month": 1, "peak_day": 3,
        "active_days_before": 5, "active_days_after": 5,
        "peak_rate": 120,
        "hemisphere": "north",
        "radiant": "Boötes",
        "radiant_direction": "northeast",
        "viewing_window": "2 AM to dawn",
        "speed_kms": 41,
        "source_body": "Asteroid 2003 EH1",
        "description": (
            "One of the strongest annual showers, but with a very sharp peak lasting only 6 hours. "
            "Produced by debris from asteroid 2003 EH1 (not a comet), which makes it unusual. "
            "Missing the brief peak means seeing far fewer meteors, so timing is everything."
        ),
        "viewing_tip": (
            "Face northeast and look about halfway up the sky. The radiant rises after midnight, "
            "so the best meteors come in the pre-dawn hours. Allow 20 minutes for your eyes to "
            "dark-adapt — binoculars are not needed. The meteors radiate from near the Big Dipper's handle."
        ),
    },
    {
        "name": "Lyrids",
        "peak_month": 4, "peak_day": 22,
        "active_days_before": 5, "active_days_after": 3,
        "peak_rate": 18,
        "hemisphere": "both",
        "radiant": "Lyra",
        "radiant_direction": "east-northeast",
        "viewing_window": "midnight to dawn",
        "speed_kms": 49,
        "source_body": "Comet C/1861 G1 Thatcher",
        "description": (
            "One of the oldest recorded meteor showers — observations date back 2,600 years to ancient China. "
            "Debris from Comet Thatcher, which last passed near Earth in 1861. Occasional outburst years "
            "can surprise with 100+ meteors per hour."
        ),
        "viewing_tip": (
            "Face east-northeast and look for Vega, the brightest star in that part of the sky — "
            "meteors stream outward from near it. Best after midnight when Lyra is high overhead. "
            "Lyrids are moderately fast and often leave brief glowing trains."
        ),
    },
    {
        "name": "Eta Aquariids",
        "peak_month": 5, "peak_day": 6,
        "active_days_before": 10, "active_days_after": 10,
        "peak_rate": 50,
        "hemisphere": "south",
        "radiant": "Aquarius",
        "radiant_direction": "east",
        "viewing_window": "3 AM to dawn",
        "speed_kms": 66,
        "source_body": "Comet 1P/Halley",
        "description": (
            "Debris shed by the legendary Halley's Comet on its outbound journey from the Sun. "
            "These are among the fastest meteors of any annual shower (66 km/s), often leaving "
            "long glowing trains that drift and twist for several seconds."
        ),
        "viewing_tip": (
            "Face east and look low on the horizon before dawn — the radiant in Aquarius stays "
            "low for Northern Hemisphere observers, so you may see fewer meteors than Southern Hemisphere skywatchers. "
            "Meteors will streak upward and across the sky from a low eastern point. Best viewing "
            "is in the hour before astronomical dawn."
        ),
    },
    {
        "name": "Delta Aquariids",
        "peak_month": 7, "peak_day": 30,
        "active_days_before": 15, "active_days_after": 10,
        "peak_rate": 20,
        "hemisphere": "south",
        "radiant": "Aquarius",
        "radiant_direction": "south",
        "viewing_window": "midnight to 3 AM",
        "speed_kms": 41,
        "source_body": "Comet 96P/Machholz (probable)",
        "description": (
            "A broad, steady shower that peaks around July 30 but produces meteors across several weeks. "
            "Best seen from tropical and southern latitudes where Aquarius rises higher in the sky. "
            "Often overlaps with the start of the Perseid season."
        ),
        "viewing_tip": (
            "Face south and look roughly halfway up the sky. The radiant doesn't rise very high from "
            "mid-northern latitudes, so expect lower rates than quoted. Meteors near the radiant have "
            "short trails; those further away have longer ones. Best after local midnight."
        ),
    },
    {
        "name": "Perseids",
        "peak_month": 8, "peak_day": 12,
        "active_days_before": 7, "active_days_after": 5,
        "peak_rate": 100,
        "hemisphere": "north",
        "radiant": "Perseus",
        "radiant_direction": "northeast",
        "viewing_window": "10 PM to dawn (best after midnight)",
        "speed_kms": 59,
        "source_body": "Comet 109P/Swift-Tuttle",
        "description": (
            "The most beloved annual meteor shower and a summer tradition. Debris from Comet Swift-Tuttle "
            "produces fast, bright meteors — often with vivid fireballs. Warm August nights make this "
            "the most-watched shower of the year."
        ),
        "viewing_tip": (
            "Face northeast toward the W-shape of Cassiopeia. You can start watching as early as 10 PM "
            "when Perseus clears the horizon, but rates triple after midnight once the radiant is high overhead. "
            "Lie back on a blanket and let your eyes roam across as much sky as possible — don't stare at "
            "the radiant itself. Perseids are fast and often leave glowing dust trails."
        ),
    },
    {
        "name": "Orionids",
        "peak_month": 10, "peak_day": 21,
        "active_days_before": 7, "active_days_after": 7,
        "peak_rate": 20,
        "hemisphere": "both",
        "radiant": "Orion",
        "radiant_direction": "east-southeast",
        "viewing_window": "midnight to dawn",
        "speed_kms": 66,
        "source_body": "Comet 1P/Halley",
        "description": (
            "The second annual gift from Halley's Comet — this time from debris encountered on its "
            "inbound leg. Among the fastest meteor showers (66 km/s), Orionids produce sharp, "
            "persistent trains and occasional bright fireballs."
        ),
        "viewing_tip": (
            "Face east-southeast and look above Orion's belt. The radiant rises after midnight, "
            "so the best views are from 1 AM to dawn. Meteors can appear anywhere in the sky — "
            "look 90° away from the radiant to catch meteors with the longest visible trails. "
            "Binoculars hurt more than help — use your naked eye and wide field of view."
        ),
    },
    {
        "name": "Leonids",
        "peak_month": 11, "peak_day": 17,
        "active_days_before": 5, "active_days_after": 3,
        "peak_rate": 15,
        "hemisphere": "both",
        "radiant": "Leo",
        "radiant_direction": "east",
        "viewing_window": "1 AM to dawn",
        "speed_kms": 71,
        "source_body": "Comet 55P/Tempel-Tuttle",
        "description": (
            "The fastest meteor shower in the calendar (71 km/s) and historically capable of legendary "
            "storms — in 1833 and 1966, observers saw tens of thousands per hour. Normal years produce "
            "a modest shower, but Leonids are famous for surprise outbursts every 33 years when "
            "Comet Tempel-Tuttle returns."
        ),
        "viewing_tip": (
            "Face east toward Leo — look for the backwards question-mark shape (the Sickle) with bright "
            "Regulus at its base. The radiant rises around midnight, with peak activity in the pre-dawn hours. "
            "Leonids hit the atmosphere nearly head-on, so expect very fast meteors with persistent streaks "
            "and the occasional brilliant fireball."
        ),
    },
    {
        "name": "Geminids",
        "peak_month": 12, "peak_day": 14,
        "active_days_before": 5, "active_days_after": 5,
        "peak_rate": 150,
        "hemisphere": "both",
        "radiant": "Gemini",
        "radiant_direction": "northeast to overhead",
        "viewing_window": "9 PM to dawn (best 10 PM–2 AM)",
        "speed_kms": 35,
        "source_body": "Asteroid 3200 Phaethon",
        "description": (
            "The king of meteor showers and the year's most prolific — up to 150 multicolored meteors "
            "per hour at peak. Unlike most showers, Geminids come from an asteroid (3200 Phaethon), "
            "not a comet. They're slower than most, making them easier to spot, and the radiant rises "
            "before 9 PM so you don't have to stay up until midnight."
        ),
        "viewing_tip": (
            "Face northeast and look toward the twin stars Castor and Pollux in Gemini. The radiant "
            "is usefully high as early as 9–10 PM — you get good rates before midnight, which is rare. "
            "Geminids are slower and brighter than average, often producing vivid reds, yellows, and whites. "
            "Bundle up: December nights are cold but the shower rewards patience. Peak is typically "
            "10 PM to 2 AM local time."
        ),
    },
    {
        "name": "Ursids",
        "peak_month": 12, "peak_day": 22,
        "active_days_before": 3, "active_days_after": 3,
        "peak_rate": 10,
        "hemisphere": "north",
        "radiant": "Ursa Minor",
        "radiant_direction": "north (near Polaris)",
        "viewing_window": "midnight to dawn",
        "speed_kms": 33,
        "source_body": "Comet 8P/Tuttle",
        "description": (
            "A modest Northern Hemisphere shower that coincides with the winter solstice, "
            "produced by debris from Comet 8P/Tuttle. The radiant is circumpolar — it never sets "
            "for Northern Hemisphere observers — but rates are low. Occasional outbursts can bring "
            "surprises on the solstice."
        ),
        "viewing_tip": (
            "Face north and look toward the Little Dipper — the radiant is near Polaris, the North Star. "
            "Because the radiant is circumpolar, meteors can appear anywhere in the northern sky at any hour. "
            "This is a good shower for a short late-night session since rates don't dramatically improve "
            "with the hour. Best observed 1 AM to dawn."
        ),
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
            viewing_tip = shower.get("viewing_tip", "")

            if hemisphere == "north" and lat < -20:
                quality = "poor"
                notes = (
                    f"This shower favors the Northern Hemisphere — the radiant in {shower['radiant']} "
                    f"stays below the horizon or very low from your latitude."
                )
            elif hemisphere == "south" and lat > 20:
                quality = "fair"
                notes = (
                    f"Best viewed from the Southern Hemisphere. From your latitude the radiant in "
                    f"{shower['radiant']} is low on the horizon, reducing visible rates. "
                    f"Face {shower.get('radiant_direction', 'the radiant constellation')} and look low — "
                    f"best between {shower.get('viewing_window', 'midnight and dawn')}."
                )
            else:
                dir_phrase = shower.get("radiant_direction", "the radiant")
                quality = "excellent"
                notes = (
                    f"Face {dir_phrase}, look halfway up the sky. "
                    f"Best viewing: {shower.get('viewing_window', '2 AM to dawn')} local time. "
                    f"Expected rate under dark skies: up to {shower['peak_rate']} meteors/hour. "
                    f"Speed: {shower.get('speed_kms', '?')} km/s — "
                    + ("very fast, expect brief streaks." if shower.get("speed_kms", 0) >= 60
                       else "moderate speed, easier to track." if shower.get("speed_kms", 0) >= 35
                       else "slower meteors with longer visible trails.")
                )

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
                    "radiant_direction": shower.get("radiant_direction", ""),
                    "best_viewing_time": shower.get("viewing_window", "midnight to dawn"),
                    "speed_kms": shower.get("speed_kms"),
                    "source_body": shower.get("source_body", ""),
                    "hemisphere": hemisphere,
                    "viewing_tip": viewing_tip,
                },
            })

    return events
