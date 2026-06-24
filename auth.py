"""Authentication helpers: sessions, cookies, role dependencies."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Union

import bcrypt
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DbSession

from config import settings
from database import ProjectMember, Session as UserSession, User, get_db_session


def generate_token(n: int = 64) -> str:
    """Generate a URL-safe session token."""
    return secrets.token_urlsafe(n)[:64]


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def login_user(username: str, password: str, db: DbSession) -> str | None:
    """Authenticate user credentials and create a new session."""
    user = db.query(User).filter_by(username=username).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None

    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_LIFETIME_HOURS)
    session = UserSession(user_id=user.id, token=token, expires_at=expires_at)
    db.add(session)
    db.commit()
    return token


def logout_user(token: str, db: DbSession) -> None:
    """Remove a session from the database."""
    session = db.query(UserSession).filter_by(token=token).first()
    if session:
        db.delete(session)
        db.commit()


def get_current_user(
    request: Request,
    db: DbSession = Depends(get_db_session),
) -> Union[User, RedirectResponse]:
    """Resolve the current user from the session cookie or redirect to login."""
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse("/login", status_code=302)

    session = db.query(UserSession).filter_by(token=token).first()
    if not session or session.expires_at < datetime.utcnow():
        return RedirectResponse("/login", status_code=302)

    user = db.query(User).filter_by(id=session.user_id).first()
    if not user or not user.is_active:
        return RedirectResponse("/login", status_code=302)

    return user


def require_authenticated(
    user: Union[User, RedirectResponse] = Depends(get_current_user),
) -> Union[User, RedirectResponse]:
    """Require any authenticated active user."""
    return user


def require_admin(
    user: Union[User, RedirectResponse] = Depends(get_current_user),
) -> Union[User, RedirectResponse]:
    """Require an admin user."""
    if isinstance(user, RedirectResponse):
        return user
    if user.system_role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


def require_coordinator_or_admin(
    user: Union[User, RedirectResponse] = Depends(get_current_user),
) -> Union[User, RedirectResponse]:
    """Require a coordinator or admin user."""
    if isinstance(user, RedirectResponse):
        return user
    if user.system_role not in ("admin", "coordinator"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


def can_write_to_project(project_id: int, user: User, db: DbSession) -> bool:
    """Return True if the user may write to the given project."""
    if user.system_role == "admin":
        return True
    return (
        db.query(ProjectMember)
        .filter_by(project_id=project_id, user_id=user.id)
        .first()
        is not None
    )
