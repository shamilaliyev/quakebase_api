from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Earthquake(Base):
    __tablename__ = "earthquakes"

    id = Column(Integer, primary_key=True, index=True)
    usgs_id = Column(String(120), unique=True, nullable=True, index=True)
    place = Column(String(500), nullable=False, index=True)
    magnitude = Column(Float, nullable=True, index=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    depth = Column(Float, nullable=True)
    status = Column(String(80), nullable=True)
    tsunami = Column(Boolean, default=False, nullable=False, index=True)
    earthquake_type = Column(String(80), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
