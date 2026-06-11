from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.database import init_db
from app.routers import auth, earthquakes


app = FastAPI(
    title="QuakeBase API",
    description=(
        "QuakeBase API is a backend API for global earthquake data. "
        "Public users can read earthquake records with pagination and filters. "
        "Authenticated users can create, update, and delete earthquake records."
    ),
    version="1.0.0",
    contact={"name": "Shamil Aliyev"},
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to QuakeBase API",
        "docs": "/docs",
        "health": "API is running",
    }


app.include_router(auth.router)
app.include_router(earthquakes.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(app, title=app.title, version=app.version, description=app.description)
    # Ensure an OAuth2 password flow is available in the OpenAPI components
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes.setdefault("OAuth2Password", {
        "type": "oauth2",
        "flows": {"password": {"tokenUrl": "/auth/login", "scopes": {}}},
    })
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
