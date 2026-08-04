"""Backend startup script."""

import os
import sys

if sys.stdout and sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if sys.stderr and sys.stderr.encoding != "utf-8":
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn
from app.config import get_settings


def _env_flag_enabled(name: str) -> bool:
    value = os.getenv(name, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def build_uvicorn_options(settings=None) -> dict:
    settings = settings or get_settings()
    return {
        "app": "app.api.main:app",
        "host": settings.host,
        "port": settings.port,
        "reload": _env_flag_enabled("UVICORN_RELOAD") or _env_flag_enabled("RELOAD"),
        "log_level": settings.log_level.lower(),
    }


if __name__ == "__main__":
    uvicorn.run(**build_uvicorn_options())
