"""
Firebase Cloud Messaging sender for native iOS/Android push notifications.
FCM routes to APNs on iOS — no APNs certificates needed on the backend.
Requires FIREBASE_CREDENTIALS_JSON env var set to the service account JSON string.
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)
_app = None


def _get_app():
    global _app
    if _app is not None:
        return _app

    from ..config import settings
    if not settings.FIREBASE_CREDENTIALS_JSON:
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(cred_dict)
        _app = firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.error("Firebase init failed: %s", e)
        return None

    return _app


def send_fcm(token: str, payload: dict) -> bool:
    app = _get_app()
    if not app:
        logger.warning("Firebase not configured — skipping FCM notification")
        return False

    try:
        from firebase_admin import messaging

        msg = messaging.Message(
            notification=messaging.Notification(
                title=payload.get("title", "Cosmic Events"),
                body=payload.get("body", ""),
            ),
            data={k: str(v) for k, v in (payload.get("data") or {}).items()},
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound="default",
                        content_available=True,
                    )
                )
            ),
            token=token,
        )
        messaging.send(msg, app=app)
        return True
    except Exception as e:
        logger.error("FCM send failed for token %s…: %s", token[:20], e)
        return False
