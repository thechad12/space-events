"""
Web Push notification sender using VAPID keys and pywebpush.
"""
import json
import logging
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)


def send_push(endpoint: str, p256dh: str, auth: str, payload: dict) -> bool:
    """
    Send a single Web Push notification. Returns True on success.
    Requires VAPID_PRIVATE_KEY and VAPID_PUBLIC_KEY set in environment.
    """
    if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
        logger.warning("VAPID keys not configured — skipping push notification")
        return False

    try:
        from pywebpush import webpush, WebPushException

        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {"p256dh": p256dh, "auth": auth},
            },
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": f"mailto:{settings.VAPID_CLAIM_EMAIL}",
            },
        )
        return True
    except Exception as e:
        logger.error("Push send failed for %s: %s", endpoint[:40], e)
        return False


def build_event_payload(event: dict, location_name: str) -> dict:
    type_emoji = {
        "rocket_launch": "🚀",
        "meteor_shower": "☄️",
        "aurora": "🌌",
        "lunar_eclipse": "🌕",
        "solar_eclipse": "☀️",
        "planetary": "🪐",
        "comet": "💫",
    }.get(event["type"], "🔭")

    quality = event.get("visibility", {}).get("quality", "")
    quality_label = {"excellent": "Excellent", "good": "Good", "fair": "Fair"}.get(quality, "")

    from datetime import datetime
    start = datetime.fromisoformat(event["start_date"])
    time_str = start.strftime("%-I:%M %p UTC") if hasattr(start, "strftime") else str(start)

    return {
        "title": f"{type_emoji} {event['name']}",
        "body": f"{quality_label} visibility from {location_name} — {time_str}\n{event['visibility']['notes'][:120]}",
        "icon": "/favicon.svg",
        "badge": "/favicon.svg",
        "tag": event["id"],
        "data": {
            "event_id": event["id"],
            "event_type": event["type"],
            "url": "/",
        },
    }
