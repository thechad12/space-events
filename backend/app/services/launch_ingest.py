"""
Background ingestion of Launch Library 2 launches into the bitemporal
`event` / `event_fact` tables.

Idempotency
-----------
- `event` is keyed by (source, source_ref), so a launch is inserted once.
- Each upstream record is reduced to a normalized payload and hashed. If the
  hash matches the current fact, nothing is written, so polling the same data
  over and over is a no-op.

Bitemporal update
-----------------
`valid` is when a schedule held in the world, `recorded` is when we believed it.
When a launch changes at time T (we learn of it at transaction time `now`):

    before:  F  valid [v0, inf)  recorded [r0, inf)     <- current belief

    after:   F  valid [v0, inf)  recorded [r0, now)     <- what we used to think
             F' valid [v0, T)    recorded [now, inf)    <- old schedule held until T
             N  valid [T, inf)   recorded [now, inf)    <- new schedule from T on

T is LL2's `last_updated`, clamped to [v0, now]. Querying with a valid time and
a recorded time ("what did we think on Monday the NET was on Sunday?") is
`launch_fact_as_of`.

Once a launch flies, LL2's status becomes Success/Failure and `net` is the
actual liftoff time, so the same mechanism records the actual launch as the
last fact. Recently flown launches drop out of /upcoming, so /previous is
polled for a short lookback to catch that final update.
"""
import asyncio
import hashlib
import json
import logging
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from sqlalchemy import Boolean, func, select
from sqlalchemy.dialects.postgresql import Range, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.event import Event
from ..models.event_actual import EventFact

logger = logging.getLogger(__name__)

SOURCE = "ll2"
EVENT_TYPE = "launch"
LL2_LAUNCHES_URL = "https://ll.thespacedevs.com/2.2.0/launches"
USER_AGENT = "LookUp/1.0"
PAGE_LIMIT = 100
PREVIOUS_LOOKBACK = timedelta(days=3)

# LL2 status abbrev -> our status vocabulary.
_STATUS_MAP = {
    "go": "go",
    "tbd": "tbd",
    "tbc": "tbd",
    "hold": "hold",
    "in flight": "go",
    "success": "success",
    "failure": "failure",
    "partial failure": "failure",
}

# LL2 net_precision name -> our precision vocabulary. When LL2 is finer than
# what we can express we round *coarser*, never finer.
_PRECISION_MAP = {
    "second": "second",
    "minute": "hour",
    "hour": "hour",
    "morning": "day",
    "afternoon": "day",
    "day": "day",
}
_DEFAULT_PRECISION = "hour"   # LL2 omitted it
_COARSE_PRECISION = "month"   # week, month, quarter, half, year...


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #

def _parse_dt(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(value: Any) -> Optional[str]:
    dt = _parse_dt(value)
    return dt.isoformat() if dt else None


def _float(value: Any) -> Optional[float]:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def normalize_launch(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an LL2 launch to the fields we track.

    Bookkeeping fields that change without the launch changing (`last_updated`,
    `url`, the various *_count fields) are left out so they don't produce new
    facts. Timestamps are canonicalised to UTC and empty strings to None so
    formatting noise doesn't change the hash.
    """
    mission = raw.get("mission") or {}
    orbit = mission.get("orbit") or {}
    rocket_cfg = (raw.get("rocket") or {}).get("configuration") or {}
    pad = raw.get("pad") or {}
    pad_loc = pad.get("location") or {}
    provider = raw.get("launch_service_provider") or {}
    status = raw.get("status") or {}
    precision = raw.get("net_precision") or {}

    return {
        "id": str(raw["id"]),
        "name": raw.get("name") or None,
        "net": _iso(raw.get("net")),
        "net_precision": precision.get("name") or None,
        "window_start": _iso(raw.get("window_start")),
        "window_end": _iso(raw.get("window_end")),
        "status": status.get("abbrev") or None,
        "status_name": status.get("name") or None,
        "probability": raw.get("probability"),
        "holdreason": raw.get("holdreason") or None,
        "failreason": raw.get("failreason") or None,
        "provider": provider.get("name") or None,
        "rocket": rocket_cfg.get("full_name") or None,
        "mission": {
            "name": mission.get("name") or None,
            "description": mission.get("description") or None,
            "type": mission.get("type") or None,
            "orbit": orbit.get("abbrev") or None,
        },
        "pad": {
            "id": pad.get("id"),
            "name": pad.get("name") or None,
            "latitude": _float(pad.get("latitude") or pad_loc.get("latitude")),
            "longitude": _float(pad.get("longitude") or pad_loc.get("longitude")),
            "location": pad_loc.get("name") or None,
        },
        "image": raw.get("image") or None,
        "webcast_live": bool(raw.get("webcast_live")),
    }


def payload_hash(payload: Dict[str, Any]) -> bytes:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).digest()


def _map_status(payload: Dict[str, Any]) -> str:
    return _STATUS_MAP.get((payload.get("status") or "").lower(), "tbd")


def _map_precision(payload: Dict[str, Any]) -> str:
    name = (payload.get("net_precision") or "").lower()
    if not name:
        return _DEFAULT_PRECISION
    return _PRECISION_MAP.get(name, _COARSE_PRECISION)


# --------------------------------------------------------------------------- #
# Persistence
# --------------------------------------------------------------------------- #

def _open_range(lower: datetime) -> Range:
    return Range(lower, None, bounds="[)")


def _current_fact(db: Session, event_id: UUID) -> Optional[EventFact]:
    """The fact we currently believe and that is still in effect (both ranges open)."""
    return db.execute(
        select(EventFact)
        .where(
            EventFact.event_id == event_id,
            func.upper_inf(EventFact.recorded, type_=Boolean),
            func.upper_inf(EventFact.valid, type_=Boolean),
        )
        .with_for_update()
    ).scalar_one_or_none()


def ingest_one(db: Session, raw: Dict[str, Any]) -> str:
    """Apply one LL2 launch. Returns 'created', 'updated' or 'unchanged'.

    Runs inside the caller's transaction; the caller commits.
    """
    payload = normalize_launch(raw)
    source_ref = payload["id"]
    digest = payload_hash(payload)

    db.execute(
        insert(Event)
        .values(
            event_id=Event.make_id(SOURCE, source_ref),
            source=SOURCE,
            source_ref=source_ref,
            event_type=EVENT_TYPE,
        )
        .on_conflict_do_nothing()
    )
    # Row lock serialises concurrent ingesters (e.g. two app instances) per launch.
    event_id = db.execute(
        select(Event.event_id)
        .where(Event.source == SOURCE, Event.source_ref == source_ref)
        .with_for_update()
    ).scalar_one()

    current = _current_fact(db, event_id)
    if current is not None and bytes(current.payload_hash) == digest:
        return "unchanged"

    # Transaction time: one value for every row this transaction writes.
    now: datetime = db.execute(select(func.now())).scalar_one()
    changed_at = min(_parse_dt(raw.get("last_updated")) or now, now)

    new_fact = EventFact(
        event_id=event_id,
        recorded=_open_range(now),
        net_start=_parse_dt(payload["net"]),
        net_precision=_map_precision(payload),
        status=_map_status(payload),
        payload=payload,
        payload_hash=digest,
    )

    if current is None:
        new_fact.valid = _open_range(changed_at)
        db.add(new_fact)
        return "created"

    old_valid_from = current.valid.lower
    changed_at = max(changed_at, old_valid_from)

    # Stop believing the open-ended version. Flush now: the exclusion
    # constraint is checked per statement, so this must land before the inserts.
    current.recorded = Range(current.recorded.lower, now, bounds="[)")
    db.flush()

    if changed_at > old_valid_from:
        # Re-assert the old schedule, now bounded by when it stopped holding.
        db.add(EventFact(
            event_id=event_id,
            valid=Range(old_valid_from, changed_at, bounds="[)"),
            recorded=_open_range(now),
            net_start=current.net_start,
            net_precision=current.net_precision,
            status=current.status,
            payload=current.payload,
            payload_hash=current.payload_hash,
        ))

    new_fact.valid = _open_range(changed_at)
    db.add(new_fact)
    return "updated"


def ingest_launches(raws: List[Dict[str, Any]]) -> Counter:
    """Apply a batch of LL2 launches, one transaction per launch."""
    counts: Counter = Counter()
    db = SessionLocal()
    try:
        for raw in raws:
            try:
                counts[ingest_one(db, raw)] += 1
                db.commit()
            except (SQLAlchemyError, KeyError, TypeError, ValueError) as e:
                db.rollback()
                counts["failed"] += 1
                logger.warning("Launch ingest failed for %s: %s", raw.get("id"), e)
    finally:
        db.close()
    return counts


def launch_fact_as_of(
    db: Session,
    event_id: UUID,
    valid_at: datetime,
    known_at: Optional[datetime] = None,
) -> Optional[EventFact]:
    """The schedule in effect at `valid_at`, as we believed it at `known_at` (default: now)."""
    known_at = known_at or datetime.now(timezone.utc)
    return db.execute(
        select(EventFact).where(
            EventFact.event_id == event_id,
            EventFact.valid.contains(valid_at),
            EventFact.recorded.contains(known_at),
        )
    ).scalar_one_or_none()


# --------------------------------------------------------------------------- #
# Fetching + job entry point
# --------------------------------------------------------------------------- #

async def _fetch(client: httpx.AsyncClient, path: str, params: Dict[str, Any]) -> List[dict]:
    resp = await client.get(
        f"{LL2_LAUNCHES_URL}/{path}/",
        params={"format": "json", "limit": PAGE_LIMIT, **params},
        headers={"User-Agent": USER_AGENT},
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


async def fetch_launches() -> List[dict]:
    """Upcoming launches plus recently flown ones, deduplicated by LL2 id.

    Two requests per run; LL2's free tier allows 15 per hour, shared with
    services/launches.py.
    """
    since = (datetime.now(timezone.utc) - PREVIOUS_LOOKBACK).isoformat()
    async with httpx.AsyncClient(timeout=20) as client:
        results = await asyncio.gather(
            _fetch(client, "upcoming", {}),
            _fetch(client, "previous", {"net__gte": since}),
            return_exceptions=True,
        )

    by_id: Dict[str, dict] = {}
    for name, result in zip(("upcoming", "previous"), results):
        if isinstance(result, Exception):
            logger.warning("LL2 %s fetch failed: %s", name, result)
            continue
        for raw in result:
            ref = raw.get("id")
            if not ref:
                continue
            ref = str(ref)
            seen = by_id.get(ref)
            # A launch can appear in both lists; keep the freshest copy.
            stamp = _parse_dt(raw.get("last_updated"))
            if seen is None or (stamp and stamp > (_parse_dt(seen.get("last_updated")) or stamp)):
                by_id[ref] = raw
    return list(by_id.values())


async def run_launch_ingest() -> None:
    """Scheduler job: fetch from LL2 and record any changes."""
    try:
        raws = await fetch_launches()
        if not raws:
            return
        counts = await asyncio.to_thread(ingest_launches, raws)
        logger.info("Launch ingest: %s", dict(counts))
    except Exception:
        logger.exception("Launch ingest run failed")
