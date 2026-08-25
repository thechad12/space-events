from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
from ..database import get_db
from ..models.user import User
from ..models.location import UserLocation
from ..schemas.location import LocationCreate, LocationUpdate, LocationOut, GeocodeResult
from ..cache import cache_get, cache_set
from .deps import get_current_user

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=List[LocationOut])
def list_locations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(UserLocation).filter(UserLocation.user_id == current_user.id).all()


@router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.is_default:
        db.query(UserLocation).filter(UserLocation.user_id == current_user.id).update({"is_default": False})

    loc = UserLocation(user_id=current_user.id, **payload.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.patch("/{location_id}", response_model=LocationOut)
def update_location(
    location_id: int,
    payload: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loc = db.query(UserLocation).filter(UserLocation.id == location_id, UserLocation.user_id == current_user.id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    if payload.is_default:
        db.query(UserLocation).filter(UserLocation.user_id == current_user.id).update({"is_default": False})

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loc, field, value)
    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loc = db.query(UserLocation).filter(UserLocation.id == location_id, UserLocation.user_id == current_user.id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()


@router.get("/geocode/search", response_model=List[GeocodeResult])
async def geocode_search(q: str):
    cache_key = f"geocode:{q.lower().strip()}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5, "addressdetails": 0},
            headers={"User-Agent": "LookUp/1.0"},
            timeout=10,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Geocoding service unavailable")

    results = []
    for r in resp.json():
        results.append(GeocodeResult(
            name=r.get("display_name", q)[:60],
            lat=float(r["lat"]),
            lng=float(r["lon"]),
            display_name=r.get("display_name", q),
        ))

    cache_set(cache_key, [r.model_dump() for r in results], ttl=3600)
    return results
