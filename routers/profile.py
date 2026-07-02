"""User profile routes."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as DbSession

from auth import get_current_user, get_unread_count, hash_password, verify_password
from database import User, get_db_session
from limiter import limiter
from utils.nav import nav_context

router = APIRouter(tags=["profile"])
templates = Jinja2Templates(directory="templates")


@router.get("/profile")
async def profile_page(
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the user profile and password change form."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "current_user": current_user,
            "msg": request.query_params.get("msg"),
            "error": request.query_params.get("error"),
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db),
        },
    )


@router.post("/profile/password")
@limiter.limit("5/minute")
async def profile_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Change the authenticated user's password."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not verify_password(current_password, current_user.password_hash):
        return RedirectResponse("/profile?error=wrong_password", status_code=303)
    if len(new_password) < 6:
        return RedirectResponse("/profile?error=too_short", status_code=303)
    if new_password != confirm_password:
        return RedirectResponse("/profile?error=mismatch", status_code=303)

    user = db.query(User).filter_by(id=current_user.id).first()
    if user:
        user.password_hash = hash_password(new_password)
        db.commit()

    return RedirectResponse("/profile?msg=changed", status_code=303)
