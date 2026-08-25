"""
APScheduler background jobs for push notifications.
Runs twice daily, dispatching to both:
  - Web Push (VAPID) for browser/PWA subscribers
  - FCM (Firebase) for native iOS/Android subscribers
"""
import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models.push_subscription import PushSubscription
from .models.fcm_token import FcmToken
from .models.location import UserLocation
from .services.astronomy import get_events_for_location
from .notifications.push import send_push, build_event_payload
from .notifications.fcm import send_fcm

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

NOTIFY_HOURS_BEFORE = 24  # default for FCM tokens (no per-token preference yet)


async def _events_for_user_locations(user_id: int, db: Session, hours_window: int):
    """Yield (location, event) pairs visible within the next `hours_window` hours."""
    now = datetime.now(timezone.utc)
    locations = db.query(UserLocation).filter(UserLocation.user_id == user_id).all()
    for loc in locations:
        window_end = (now + timedelta(hours=hours_window + 2)).date()
        try:
            events = await get_events_for_location(loc.lat, loc.lng, now.date(), window_end)
        except Exception as e:
            logger.error("Event fetch failed for location %d: %s", loc.id, e)
            continue

        for event in events:
            if not event.get("visibility", {}).get("visible"):
                continue
            try:
                event_start = datetime.fromisoformat(event["start_date"])
                if event_start.tzinfo is None:
                    event_start = event_start.replace(tzinfo=timezone.utc)
                hours_until = (event_start - now).total_seconds() / 3600
            except Exception:
                continue
            if 0 < hours_until <= hours_window:
                yield loc, event


async def _dispatch_web_push(db: Session):
    subs = db.query(PushSubscription).filter(PushSubscription.is_active == True).all()
    for sub in subs:
        async for loc, event in _events_for_user_locations(sub.user_id, db, sub.notify_hours_before):
            payload = build_event_payload(event, loc.name)
            ok = send_push(sub.endpoint, sub.p256dh, sub.auth, payload)
            if not ok:
                sub.is_active = False
                db.commit()
                break


async def _dispatch_fcm(db: Session):
    tokens = db.query(FcmToken).filter(FcmToken.is_active == True).all()
    for token_row in tokens:
        async for loc, event in _events_for_user_locations(token_row.user_id, db, NOTIFY_HOURS_BEFORE):
            payload = build_event_payload(event, loc.name)
            ok = send_fcm(token_row.token, payload)
            if not ok:
                token_row.is_active = False
                db.commit()
                break


async def _dispatch_notifications():
    db: Session = SessionLocal()
    try:
        await _dispatch_web_push(db)
        await _dispatch_fcm(db)
    except Exception as e:
        logger.error("Notification dispatch error: %s", e)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        _dispatch_notifications,
        trigger="cron",
        hour="7,19",
        minute=0,
        id="push_notifications",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Notification scheduler started")


def stop_scheduler():
    scheduler.shutdown(wait=False)
