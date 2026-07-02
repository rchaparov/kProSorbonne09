"""TeamSpace application entry point."""

import os
import time
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded

from auth import _RedirectException
from config import settings, validate_settings
from database import Session as UserSession, SessionLocal, TempFileToken, init_database
from limiter import limiter

validate_settings()

app = FastAPI(title="K-PRO Sorbonne 09 TeamSpace", docs_url=None, redoc_url=None)
app.state.limiter = limiter
templates = Jinja2Templates(directory="templates")
STATIC_VERSION = os.environ.get("RAILWAY_GIT_COMMIT_SHA", str(int(time.time())))[:8]
templates.env.globals["static_version"] = STATIC_VERSION

app.mount("/static", StaticFiles(directory="static"), name="static")

from routers.admin import router as admin_router
from routers.analytics import router as analytics_router
from routers.auth_router import router as auth_router
from routers.checklist import router as checklist_router
from routers.dashboard import router as dashboard_router
from routers.feed import router as feed_router
from routers.files_temp import router as files_temp_router
from routers.materials import router as materials_router
from routers.notes import router as notes_router
from routers.notifications import router as notifications_router
from routers.profile import router as profile_router
from routers.projects import router as projects_router
from routers.search import router as search_router

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(projects_router)
app.include_router(feed_router)
app.include_router(checklist_router)
app.include_router(notes_router)
app.include_router(admin_router)
app.include_router(profile_router)
app.include_router(notifications_router)
app.include_router(materials_router)
app.include_router(search_router)
app.include_router(files_temp_router)


@app.exception_handler(_RedirectException)
async def redirect_handler(request: Request, exc: _RedirectException):
    """Redirect unauthenticated HTML requests to login."""
    return RedirectResponse(exc.url, status_code=302)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Render login page when login rate limit is exceeded."""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "current_user": None,
            "error": "rate_limited",
            "unread_count": 0,
        },
        status_code=429,
    )


@app.on_event("startup")
async def startup() -> None:
    """Initialize database engine, session factory, and clean expired sessions."""
    init_database(settings.DATABASE_URL)
    if SessionLocal is None:
        return

    db = SessionLocal()
    try:
        deleted = (
            db.query(UserSession)
            .filter(UserSession.expires_at < datetime.utcnow())
            .delete()
        )
        tokens_deleted = (
            db.query(TempFileToken)
            .filter(TempFileToken.expires_at < datetime.utcnow())
            .delete()
        )
        db.commit()
        print(f"Cleaned {deleted} expired sessions")
        print(f"Cleaned {tokens_deleted} expired temp file tokens")
    finally:
        db.close()


@app.exception_handler(404)
async def not_found(request: Request, exc: Exception):
    """Redirect unknown pages to home; return JSON for file token API."""
    if request.url.path.startswith("/files/"):
        detail = getattr(exc, "detail", "Not found")
        return JSONResponse({"detail": detail}, status_code=404)
    return RedirectResponse("/")


@app.exception_handler(403)
async def forbidden(request: Request, exc: Exception):
    """Render forbidden page for access denied errors."""
    return templates.TemplateResponse(
        "403.html",
        {"request": request, "current_user": None},
        status_code=403,
    )
