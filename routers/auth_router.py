"""Authentication routes: login, logout, health check."""

from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session as DbSession

from auth import login_user, logout_user
from database import Session as UserSession, User, get_db_session
from limiter import limiter

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def login_page(
    request: Request,
    error: str | None = None,
    db: DbSession = Depends(get_db_session),
):
    """Render the login form."""
    token = request.cookies.get("session_token")
    if token:
        session = db.query(UserSession).filter_by(token=token).first()
        if session and session.expires_at >= datetime.utcnow():
            user = db.query(User).filter_by(id=session.user_id).first()
            if user and user.is_active:
                return RedirectResponse("/", status_code=302)

    error = error or request.query_params.get("error")
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
@limiter.limit("5/minute")
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
async def health(db: DbSession = Depends(get_db_session)):
    """Health check endpoint with database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        return JSONResponse(
            {"status": "error", "detail": "db unavailable"},
            status_code=503,
        )
