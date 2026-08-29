"""
Admin endpoints for managing white-label tenants.
Protected by X-Admin-Key header — set ADMIN_KEY in backend env vars.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models.tenant import Tenant
from ..config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_admin_key: str = Header(...)):
    if not settings.ADMIN_KEY or x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")


class TenantIn(BaseModel):
    hostname: str               # e.g. "sky.marriottmaui.com"
    brand_name: str             # e.g. "Marriott Maui Stargazing"
    logo_url: Optional[str] = None
    primary_color: str = "#7c3aed"
    property_name: Optional[str] = None
    default_lat: Optional[float] = None
    default_lng: Optional[float] = None
    contact_email: Optional[str] = None
    show_notifications: bool = True
    show_ar_mode: bool = True


class TenantOut(BaseModel):
    id: int
    hostname: str
    brand_name: str
    logo_url: Optional[str]
    primary_color: str
    property_name: Optional[str]
    default_lat: Optional[float]
    default_lng: Optional[float]
    contact_email: Optional[str]
    show_notifications: bool
    show_ar_mode: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/tenants", response_model=List[TenantOut], dependencies=[Depends(require_admin)])
def list_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()


@router.post("/tenants", response_model=TenantOut, status_code=201, dependencies=[Depends(require_admin)])
def create_tenant(payload: TenantIn, db: Session = Depends(get_db)):
    existing = db.query(Tenant).filter(Tenant.hostname == payload.hostname).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Tenant '{payload.hostname}' already exists")

    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.put("/tenants/{hostname}", response_model=TenantOut, dependencies=[Depends(require_admin)])
def update_tenant(hostname: str, payload: TenantIn, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.hostname == hostname).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(tenant, k, v)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/tenants/{hostname}", status_code=204, dependencies=[Depends(require_admin)])
def deactivate_tenant(hostname: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.hostname == hostname).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.is_active = False
    db.commit()
