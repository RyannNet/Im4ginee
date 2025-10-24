from __future__ import annotations
import os
from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Base, engine, get_db
from .models import User
from .security import get_password_hash
from .api.v1 import auth as auth_router
from .api.v1 import generate as generate_router
from .api.v1 import admin as admin_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Local AI Generator", version="1.0.0")

    # CORS
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router.router)
    app.include_router(generate_router.router)
    app.include_router(admin_router.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()


# Initialize DB on import
Base.metadata.create_all(bind=engine)


# Create default admin in dev
settings = get_settings()
if settings.ENV == "dev":
    from .db import session_scope

    with session_scope() as s:
        if not s.query(User).filter(User.email == "admin@example.com").first():
            s.add(User(email="admin@example.com", password_hash=get_password_hash("admin123"), is_admin=True))
