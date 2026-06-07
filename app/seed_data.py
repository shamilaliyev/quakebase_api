"""Seed the database with at least 1,000 earthquake records.

Run:
    python -m app.seed_data

The script first tries to download real data from the USGS Earthquake Catalog API.
If that fails, it generates 1,200 realistic sample records so the project still works.
"""

import random
from datetime import datetime, timedelta, timezone
from typing import Iterable, List
import requests
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal, init_db
from app.models import Earthquake

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
TARGET_COUNT = 1200


def fetch_usgs_earthquakes() -> List[dict]:
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=730)

    params = {
        "format": "geojson",
        "starttime": start_time.date().isoformat(),
        "endtime": end_time.date().isoformat(),
        "limit": 20000,
        "orderby": "time",
    }

    response = requests.get(USGS_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    features = data.get("features", [])
    return features[:TARGET_COUNT]


def convert_usgs_feature(feature: dict) -> Earthquake:
    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})
    coordinates = geometry.get("coordinates", [0, 0, 0])

    longitude = float(coordinates[0])
    latitude = float(coordinates[1])
    depth = float(coordinates[2]) if len(coordinates) > 2 and coordinates[2] is not None else None

    timestamp_ms = properties.get("time")
    quake_time = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc) if timestamp_ms else datetime.now(timezone.utc)

    return Earthquake(
        usgs_id=feature.get("id"),
        place=properties.get("place") or "Unknown location",
        magnitude=properties.get("mag"),
        time=quake_time,
        latitude=latitude,
        longitude=longitude,
        depth=depth,
        status=properties.get("status"),
        tsunami=bool(properties.get("tsunami", 0)),
        earthquake_type=properties.get("type") or "earthquake",
    )


def generate_sample_earthquakes(count: int = TARGET_COUNT) -> Iterable[Earthquake]:
    places = [
        "Alaska Peninsula",
        "Southern California",
        "Japan region",
        "Chile-Argentina border region",
        "Indonesia",
        "Turkey",
        "Greece",
        "Azerbaijan region",
        "New Zealand",
        "Philippines",
    ]
    statuses = ["reviewed", "automatic"]
    types = ["earthquake", "quarry blast", "ice quake", "explosion"]
    now = datetime.now(timezone.utc)

    for i in range(count):
        yield Earthquake(
            usgs_id=f"sample-{i + 1}",
            place=random.choice(places),
            magnitude=round(random.uniform(1.0, 7.8), 1),
            time=now - timedelta(hours=i * random.randint(1, 8)),
            latitude=round(random.uniform(-60.0, 70.0), 6),
            longitude=round(random.uniform(-170.0, 170.0), 6),
            depth=round(random.uniform(1.0, 650.0), 2),
            status=random.choice(statuses),
            tsunami=random.choice([False, False, False, True]),
            earthquake_type=random.choice(types),
        )


def save_earthquakes(earthquakes: Iterable[Earthquake]) -> int:
    db = SessionLocal()
    inserted = 0
    try:
        for earthquake in earthquakes:
            if earthquake.usgs_id:
                exists = db.query(Earthquake).filter(Earthquake.usgs_id == earthquake.usgs_id).first()
                if exists:
                    continue
            db.add(earthquake)
            try:
                db.commit()
                inserted += 1
            except IntegrityError:
                db.rollback()
        return inserted
    finally:
        db.close()


def main():
    init_db()
    try:
        print("Downloading earthquake records from USGS...")
        features = fetch_usgs_earthquakes()
        if len(features) < 1000:
            raise RuntimeError(f"USGS returned only {len(features)} records")
        earthquakes = [convert_usgs_feature(feature) for feature in features]
        inserted = save_earthquakes(earthquakes)
        print(f"Done. Inserted {inserted} real earthquake records.")
    except Exception as exc:
        print(f"Could not fetch enough USGS data: {exc}")
        print("Generating sample earthquake records instead...")
        inserted = save_earthquakes(generate_sample_earthquakes())
        print(f"Done. Inserted {inserted} sample earthquake records.")


if __name__ == "__main__":
    main()
