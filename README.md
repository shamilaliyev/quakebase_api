# QuakeBase API

QuakeBase API is a backend application for global earthquake data. It supports:

- public read access for earthquake listings and details
- authenticated creation, update, and deletion of earthquake records
- pagination, filtering, and caching
- JWT authentication with OAuth2 Bearer tokens

**Author:** Shamil Aliyev

---

## Highlights

- FastAPI backend with Swagger UI at `/docs`
- Public `GET /earthquakes` and `GET /earthquakes/{id}`
- Protected `POST`, `PUT`, `PATCH`, and `DELETE` endpoints
- Pagination with a hard maximum of 20 records per request
- Optional Redis caching with graceful fallback
- Automatic database table creation on startup
- Seed script with at least 1,000 earthquake records
- Docker-ready deployment

---

## Repository Structure

```text
quakebase_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth_utils.py
│   ├── cache.py
│   ├── seed_data.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       └── earthquakes.py
├── requirements.txt
├── Dockerfile
├── README.md
├── .env.example
└── .gitignore
```

---

## Local Setup

### 1. Open the project

```bash
cd quakebase_api
```

### 2. Create a Python virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your settings. For local development, leave `DATABASE_URL` unset to use SQLite.

Example PostgreSQL configuration:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/quakebase_db
SECRET_KEY=replace-with-a-long-random-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

Open the service at:

```text
http://127.0.0.1:8000
```

Swagger docs are available at:

```text
http://127.0.0.1:8000/docs
```

---

## Seed the Database

Populate the database with earthquake records:

```bash
python -m app.seed_data
```

The script attempts to download real earthquake data from the USGS API. If that fails or returns fewer than 1,000 records, it generates 1,200 sample records.

---

## Environment Variables

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/quakebase_db
SECRET_KEY=replace-with-a-long-random-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
```

Notes:

- `DATABASE_URL` is optional; the app defaults to local SQLite when unset.
- `SECRET_KEY` is required for JWT signing.
- `REDIS_URL` is optional. The API continues to work without Redis.

---

## API Endpoints

### Root

| Method | Path | Auth Required | Description |
|---|---|---|---|
| GET | `/` | No | API welcome and health check |

### Authentication

| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login and receive a JWT token |
| GET | `/auth/me` | Yes | Get current authenticated user |

### Earthquakes

| Method | Path | Auth Required | Description |
|---|---|---|---|
| GET | `/earthquakes` | No | List earthquakes with pagination and filters |
| GET | `/earthquakes/{earthquake_id}` | No | Get earthquake details |
| POST | `/earthquakes` | Yes | Create a new earthquake record |
| PUT | `/earthquakes/{earthquake_id}` | Yes | Replace an earthquake record |
| PATCH | `/earthquakes/{earthquake_id}` | Yes | Partially update an earthquake record |
| DELETE | `/earthquakes/{earthquake_id}` | Yes | Delete an earthquake record |

---

## Pagination and Filters

`GET /earthquakes` supports the following query parameters:

- `page` (default: `1`)
- `limit` (default: `20`, maximum: `20`)
- `min_magnitude`
- `max_magnitude`
- `place`
- `earthquake_type`
- `tsunami`

Example:

```http
GET /earthquakes?page=1&limit=20&min_magnitude=4&place=Japan
```

Response format:

```json
{
  "page": 1,
  "limit": 20,
  "total": 1200,
  "data": []
}
```

---

## Authentication Flow

Register a new user:

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "TestPass123"
}
```

Login:

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

```text
username=testuser&password=TestPass123
```

Successful response:

```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

Use the token in protected requests:

```http
Authorization: Bearer <access_token>
```

---

## Docker

Build the Docker image:

```bash
docker build -t quakebase-api .
```

Run the container:

```bash
docker run -p 8000:8000 quakebase-api
```

Open the app at:

```text
http://127.0.0.1:8000
```

Swagger docs at:

```text
http://127.0.0.1:8000/docs
```

---

## Notes

- Local SQLite is supported by default for quick development.
- Redis caching is optional and does not prevent the API from running.
- Database tables are created automatically on startup.
