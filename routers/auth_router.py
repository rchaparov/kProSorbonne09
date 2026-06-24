"""Authentication routes: login, logout, health check."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as DbSession

from auth import login_user, logout_user
from database import get_db_session

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def login_page(request: Request, error: str | None = None):
    """Render the login form."""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "current_user": None,
            "error": error,
            "unread_count": 0,
        },
    )


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: DbSession = Depends(get_db_session),
):
    """Authenticate credentials and set session cookie."""
    token = login_user(username, password, db)
    if not token:
        return RedirectResponse("/login?error=1", status_code=302)

    response = RedirectResponse("/", status_code=302)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/logout")
async def logout(
    request: Request,
    db: DbSession = Depends(get_db_session),
):
    """Clear session cookie and remove session from database."""
    token = request.cookies.get("session_token")
    if token:
        logout_user(token, db)

    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("session_token")
    return response


@router.get("/health")
async def health():
    """Health check endpoint for Railway."""
    return {"status": "ok"}
