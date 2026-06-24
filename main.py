"""TeamSpace application entry point."""

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings, validate_settings
from database import init_database
from routers.admin import router as admin_router
from routers.auth_router import router as auth_router
from routers.dashboard import router as dashboard_router
from routers.materials import router as materials_router
from routers.notes import router as notes_router
from routers.notifications import router as notifications_router
from routers.profile import router as profile_router
from routers.projects import router as projects_router

validate_settings()

app = FastAPI(title="K-PRO Sorbonne 09 TeamSpace", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(projects_router)
app.include_router(notes_router)
app.include_router(admin_router)
app.include_router(profile_router)
app.include_router(notifications_router)
app.include_router(materials_router)


@app.on_event("startup")
async def startup() -> None:
    """Initialize database engine and session factory."""
    init_database(settings.DATABASE_URL)


@app.exception_handler(404)
async def not_found(request: Request, exc: Exception) -> RedirectResponse:
    """Redirect unknown pages to home."""
    return RedirectResponse("/")


@app.exception_handler(403)
async def forbidden(request: Request, exc: Exception):
    """Render forbidden page for access denied errors."""
    return templates.TemplateResponse(
        "403.html",
        {"request": request, "current_user": None},
        status_code=403,
    )
