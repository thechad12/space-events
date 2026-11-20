import uuid

from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base

# Fixed namespace so the same (source, source_ref) always maps to the same event_id.
EVENT_ID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "space-events:event")


class Event(Base):
    """Stable identity for an upstream event (a launch, eclipse, meteor shower...).

    One row per (source, source_ref), so re-ingesting the same upstream record is
    idempotent. Everything that can change over time lives in EventFact.
    """
    __tablename__ = "event"
    __table_args__ = (UniqueConstraint("source", "source_ref", name="event_source_source_ref_key"),)

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(Text, nullable=False)       # 'll2', 'noaa_swpc', ...
    source_ref = Column(Text, nullable=False)   # the source's own id
    event_type = Column(Text, nullable=False)   # launch, eclipse, meteor_shower...

    facts = relationship(
        "EventFact",
        back_populates="event",
        order_by="EventFact.fact_id",
        passive_deletes=True,
    )

    @staticmethod
    def make_id(source: str, source_ref: str) -> uuid.UUID:
        """Deterministic event_id, so ingestion can compute it before touching the DB."""
        return uuid.uuid5(EVENT_ID_NAMESPACE, f"{source}:{source_ref}")
