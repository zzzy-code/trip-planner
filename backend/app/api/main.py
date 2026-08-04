"""FastAPI application."""

import sys

if sys.stdout and getattr(sys.stdout, "encoding", None) != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if sys.stderr and getattr(sys.stderr, "encoding", None) != "utf-8":
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..db.models import Base
from ..db.session import engine
from ..config import get_settings, validate_config, print_config
from .routes import trip, poi, map as map_routes, trips

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="\u57fa\u4e8e HelloAgents \u6846\u67b6\u7684\u667a\u80fd\u65c5\u884c\u89c4\u5212\u52a9\u624b API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(poi.router, prefix="/api")
app.include_router(map_routes.router, prefix="/api")

_original_openapi = app.openapi


def openapi_without_version() -> dict:
    schema = _original_openapi()
    schema.get("info", {}).pop("version", None)
    return schema


app.openapi = openapi_without_version


@app.on_event("startup")
async def startup_event():
    """Application startup hook."""
    print("\n" + "=" * 60)
    print(settings.app_name)
    print("=" * 60)

    if settings.auto_create_tables:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    print_config()

    try:
        validate_config()
        print("\n\u914d\u7f6e\u9a8c\u8bc1\u901a\u8fc7")
    except ValueError as e:
        print(f"\n\u914d\u7f6e\u9a8c\u8bc1\u5931\u8d25:\n{e}")
        print("\n\u8bf7\u68c0\u67e5 .env \u6587\u4ef6\u5e76\u786e\u4fdd\u5fc5\u8981\u914d\u7f6e\u5df2\u8bbe\u7f6e")
        raise

    print("\n" + "=" * 60)
    print("API\u6587\u6863: http://localhost:8000/docs")
    print("ReDoc\u6587\u6863: http://localhost:8000/redoc")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown hook."""
    print("\n" + "=" * 60)
    print("\u5e94\u7528\u6b63\u5728\u5173\u95ed...")
    print("=" * 60 + "\n")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
    }
