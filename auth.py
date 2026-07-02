"""Authentication helpers: sessions, cookies, role dependencies."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session as DbSession

from config import settings
from database import ProjectMember, Session as UserSession, User, Notification, get_db_session


class _RedirectException(Exception):
    """Signal that the client should be redirected to a URL."""

    def __init__(self, url: str) -> None:
        self.url = url


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

    db.query(UserSession).filter_by(user_id=user.id).delete()

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
) -> User:
    """Resolve the current user from the session cookie or redirect to login."""
    token = request.cookies.get("session_token")
    if not token:
        raise _RedirectException("/login")

    session = db.query(UserSession).filter_by(token=token).first()
    if not session or session.expires_at < datetime.utcnow():
        raise _RedirectException("/login")

    user = db.query(User).filter_by(id=session.user_id).first()
    if not user or not user.is_active:
        raise _RedirectException("/login")

    return user


def require_authenticated(user: User = Depends(get_current_user)) -> User:
    """Require any authenticated active user."""
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require an admin user."""
    if user.system_role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


def require_coordinator_or_admin(user: User = Depends(get_current_user)) -> User:
    """Require a coordinator or admin user."""
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


def get_unread_count(user: User, db: DbSession) -> int:
    """Return the number of unread notifications for a user."""
    return (
        db.query(Notification)
        .filter_by(user_id=user.id, is_read=False)
        .count()
    )
