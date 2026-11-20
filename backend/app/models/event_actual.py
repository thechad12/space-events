from sqlalchemy import BigInteger, Column, DDL, DateTime, ForeignKey, LargeBinary, Text, event
from sqlalchemy.dialects.postgresql import ExcludeConstraint, JSONB, TSTZRANGE, UUID
from sqlalchemy.orm import relationship

from ..database import Base


class EventFact(Base):
    """Bitemporal schedule history for an Event.

    - valid:    when this schedule held in the world (valid time)
    - recorded: when we believed it (transaction time); an open upper bound
                means this is our current belief

    The exclusion constraint guarantees that, for one event, no two facts
    overlap in both valid time and recorded time, i.e. at any point in
    "as-of" time there is exactly one answer for any point in world time.
    Unchanged upstream data is detected via payload_hash, so re-polling does
    not create new rows.
    """
    __tablename__ = "event_fact"
    __table_args__ = (
        ExcludeConstraint(
            ("event_id", "="),
            ("valid", "&&"),
            ("recorded", "&&"),
            name="event_fact_event_id_valid_recorded_excl",
            using="gist",
        ),
    )

    fact_id = Column(BigInteger, primary_key=True, autoincrement=True)  # bigserial
    event_id = Column(UUID(as_uuid=True), ForeignKey("event.event_id"), nullable=False)
    valid = Column(TSTZRANGE, nullable=False)       # when this schedule held in the world
    recorded = Column(TSTZRANGE, nullable=False)    # when we believed it
    net_start = Column(DateTime(timezone=True), nullable=True)
    net_precision = Column(Text, nullable=False)    # second | hour | day | month
    status = Column(Text, nullable=False)           # go | tbd | hold | scrubbed | success | failure
    payload = Column(JSONB, nullable=False)
    payload_hash = Column(LargeBinary, nullable=False)  # sha256 of normalized payload (bytea)

    event = relationship("Event", back_populates="facts")


# The exclusion constraint mixes a scalar (=) with ranges (&&) in one GiST
# index, which needs btree_gist. Tables are built with create_all rather than
# migrations, so create the extension right before this table.
event.listen(
    EventFact.__table__,
    "before_create",
    DDL("CREATE EXTENSION IF NOT EXISTS btree_gist"),
)
