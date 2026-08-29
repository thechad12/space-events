from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class NotificationHistory(Base):
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    event_name = Column(String, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    # "sent" | "failed" | "clicked"
    status = Column(String, nullable=False, default="sent")

    user = relationship("User")
