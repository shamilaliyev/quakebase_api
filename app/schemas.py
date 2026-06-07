from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_admin: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EarthquakeBase(BaseModel):
    usgs_id: Optional[str] = None
    place: str = Field(..., min_length=1, max_length=500)
    magnitude: Optional[float] = None
    time: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    depth: Optional[float] = None
    status: Optional[str] = None
    tsunami: bool = False
    earthquake_type: Optional[str] = "earthquake"


class EarthquakeCreate(EarthquakeBase):
    pass


class EarthquakeUpdate(BaseModel):
    usgs_id: Optional[str] = None
    place: Optional[str] = Field(default=None, min_length=1, max_length=500)
    magnitude: Optional[float] = None
    time: Optional[datetime] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    depth: Optional[float] = None
    status: Optional[str] = None
    tsunami: Optional[bool] = None
    earthquake_type: Optional[str] = None


class EarthquakeOut(EarthquakeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedEarthquakeResponse(BaseModel):
    page: int
    limit: int
    total: int
    data: List[EarthquakeOut]
