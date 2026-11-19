from sqlalchemy import Column, Integer, String, Text, Date, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base


class Eclipse(Base):
    """Catalog of solar and lunar eclipses. Seed with: python -m app.seed_eclipses"""
    __tablename__ = "eclipses"
    __table_args__ = (UniqueConstraint("type", "date", name="uq_eclipses_type_date"),)

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)            # "solar_eclipse" | "lunar_eclipse"
    date = Column(Date, nullable=False, index=True)
    eclipse_type = Column(String, nullable=False)    # "total" | "partial" | "annular"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    path_description = Column(Text, nullable=True)
    duration_min = Column(Integer, nullable=True)
    visibility_regions = Column(JSON, nullable=False, default=list)  # e.g. ["europe", "africa"]

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "date": self.date.isoformat(),
            "eclipse_type": self.eclipse_type,
            "name": self.name,
            "description": self.description,
            "path_description": self.path_description or "",
            "duration_min": self.duration_min,
            "visibility_regions": self.visibility_regions or [],
        }
