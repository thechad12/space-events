from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models.tenant import Tenant

router = APIRouter(prefix="/tenant", tags=["tenant"])


class TenantConfig(BaseModel):
    brand_name: str
    logo_url: Optional[str]
    primary_color: str
    property_name: Optional[str]
    default_lat: Optional[float]
    default_lng: Optional[float]
    show_notifications: bool
    show_ar_mode: bool
    is_white_label: bool  # false = default Look Up! branding

    class Config:
        from_attributes = True


DEFAULT_CONFIG = TenantConfig(
    brand_name="Look Up!",
    logo_url=None,
    primary_color="#7c3aed",
    property_name=None,
    default_lat=None,
    default_lng=None,
    show_notifications=True,
    show_ar_mode=True,
    is_white_label=False,
)


@router.get("", response_model=TenantConfig)
def get_tenant_config(
    host: str = Query(..., description="Hostname from the browser (window.location.hostname)"),
    db: Session = Depends(get_db),
):
    # Strip port if present (localhost:5173 → localhost)
    hostname = host.split(":")[0]
    tenant = (
        db.query(Tenant)
        .filter(Tenant.hostname == hostname, Tenant.is_active == True)
        .first()
    )
    if not tenant:
        return DEFAULT_CONFIG

    return TenantConfig(
        brand_name=tenant.brand_name,
        logo_url=tenant.logo_url,
        primary_color=tenant.primary_color,
        property_name=tenant.property_name,
        default_lat=tenant.default_lat,
        default_lng=tenant.default_lng,
        show_notifications=tenant.show_notifications,
        show_ar_mode=tenant.show_ar_mode,
        is_white_label=True,
    )
