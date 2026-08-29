from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class BookmarkedEvent(Base):
    __tablename__ = "bookmarked_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String, nullable=False)       # e.g. "meteor_perseids_2026"
    event_type = Column(String, nullable=False)     # e.g. "meteor_shower"
    event_name = Column(String, nullable=False)
    event_date = Column(String, nullable=False)     # ISO date string, for display without re-fetching
    bookmarked_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_bookmark"),
    )
