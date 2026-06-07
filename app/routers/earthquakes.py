from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.auth_utils import get_current_user
from app.cache import get_cache, invalidate_earthquake_cache, set_cache
from app.database import get_db
from app.models import Earthquake, User
from app.schemas import EarthquakeCreate, EarthquakeOut, EarthquakeUpdate, PaginatedEarthquakeResponse

router = APIRouter(prefix="/earthquakes", tags=["Earthquakes"])


def serialize_earthquake(earthquake: Earthquake) -> dict:
    return EarthquakeOut.model_validate(earthquake).model_dump(mode="json")


@router.get("", response_model=PaginatedEarthquakeResponse)
def list_earthquakes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=20),
    min_magnitude: Optional[float] = Query(None),
    max_magnitude: Optional[float] = Query(None),
    place: Optional[str] = Query(None),
    earthquake_type: Optional[str] = Query(None),
    tsunami: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    cache_key = (
        f"earthquakes:list:page={page}:limit={limit}:min={min_magnitude}:max={max_magnitude}:"
        f"place={place}:type={earthquake_type}:tsunami={tsunami}"
    )
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    query = db.query(Earthquake)

    if min_magnitude is not None:
        query = query.filter(Earthquake.magnitude >= min_magnitude)
    if max_magnitude is not None:
        query = query.filter(Earthquake.magnitude <= max_magnitude)
    if place:
        query = query.filter(Earthquake.place.ilike(f"%{place}%"))
    if earthquake_type:
        query = query.filter(Earthquake.earthquake_type.ilike(f"%{earthquake_type}%"))
    if tsunami is not None:
        query = query.filter(Earthquake.tsunami == tsunami)

    total = query.count()
    offset = (page - 1) * limit
    earthquakes = query.order_by(Earthquake.time.desc()).offset(offset).limit(limit).all()

    response = {
        "page": page,
        "limit": limit,
        "total": total,
        "data": [serialize_earthquake(eq) for eq in earthquakes],
    }
    set_cache(cache_key, response)
    return response


@router.get("/{earthquake_id}", response_model=EarthquakeOut)
def get_earthquake(earthquake_id: int, db: Session = Depends(get_db)):
    cache_key = f"earthquakes:detail:{earthquake_id}"
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    earthquake = db.query(Earthquake).filter(Earthquake.id == earthquake_id).first()
    if not earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")

    response = serialize_earthquake(earthquake)
    set_cache(cache_key, response)
    return response


@router.post("", response_model=EarthquakeOut, status_code=status.HTTP_201_CREATED)
def create_earthquake(
    earthquake_data: EarthquakeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    earthquake = Earthquake(**earthquake_data.model_dump())
    db.add(earthquake)
    db.commit()
    db.refresh(earthquake)
    invalidate_earthquake_cache()
    return earthquake


@router.put("/{earthquake_id}", response_model=EarthquakeOut)
def replace_earthquake(
    earthquake_id: int,
    earthquake_data: EarthquakeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    earthquake = db.query(Earthquake).filter(Earthquake.id == earthquake_id).first()
    if not earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")

    for key, value in earthquake_data.model_dump().items():
        setattr(earthquake, key, value)

    db.commit()
    db.refresh(earthquake)
    invalidate_earthquake_cache()
    return earthquake


@router.patch("/{earthquake_id}", response_model=EarthquakeOut)
def update_earthquake(
    earthquake_id: int,
    earthquake_data: EarthquakeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    earthquake = db.query(Earthquake).filter(Earthquake.id == earthquake_id).first()
    if not earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")

    update_data = earthquake_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(earthquake, key, value)

    db.commit()
    db.refresh(earthquake)
    invalidate_earthquake_cache()
    return earthquake


@router.delete("/{earthquake_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_earthquake(
    earthquake_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    earthquake = db.query(Earthquake).filter(Earthquake.id == earthquake_id).first()
    if not earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")

    db.delete(earthquake)
    db.commit()
    invalidate_earthquake_cache()
    return None
