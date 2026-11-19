"""
Seed / sync the `eclipses` table from eclipse_seed_data.py.

Usage (from the backend/ directory, with DATABASE_URL set in env or .env):

    python -m app.seed_eclipses

Idempotent: each eclipse is upserted by (type, date), so re-running updates
existing rows instead of duplicating them. Rows you added directly in the
database are left untouched.
"""
import sys
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from .database import Base, SessionLocal, engine
from .eclipse_seed_data import ECLIPSE_CATALOG
from .models import Eclipse

_FIELDS = ("eclipse_type", "name", "description", "path_description", "duration_min", "visibility_regions")


def _row(e: dict) -> dict:
    return {
        "type": e["type"],
        "date": date.fromisoformat(e["date"]),
        "eclipse_type": e["eclipse_type"],
        "name": e["name"],
        "description": e["description"],
        "path_description": e.get("path_description"),
        "duration_min": e.get("duration_min"),
        "visibility_regions": e.get("visibility_regions", []),
    }


def seed() -> int:
    # Make sure the table exists even if the API hasn't started against this DB yet.
    Base.metadata.create_all(bind=engine, tables=[Eclipse.__table__])

    stmt = insert(Eclipse).values([_row(e) for e in ECLIPSE_CATALOG])
    stmt = stmt.on_conflict_do_update(
        constraint="uq_eclipses_type_date",
        set_={**{f: stmt.excluded[f] for f in _FIELDS}, "updated_at": func.now()},
    )

    with SessionLocal() as db:
        db.execute(stmt)
        db.commit()
        total = db.scalar(select(func.count()).select_from(Eclipse))

    print(f"Synced {len(ECLIPSE_CATALOG)} eclipses from seed data; {total} rows in 'eclipses'.")
    return 0


if __name__ == "__main__":
    sys.exit(seed())
