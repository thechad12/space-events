from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True, nullable=False)

    # Branding
    brand_name = Column(String, nullable=False, default="Look Up!")
    logo_url = Column(String, nullable=True)
    primary_color = Column(String, nullable=False, default="#7c3aed")  # hex

    # Property info (shown in UI and used as default location)
    property_name = Column(String, nullable=True)
    default_lat = Column(Float, nullable=True)
    default_lng = Column(Float, nullable=True)
    contact_email = Column(String, nullable=True)

    # Feature flags
    show_notifications = Column(Boolean, default=True)
    show_ar_mode = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
