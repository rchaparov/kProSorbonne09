"""SQLAlchemy models and database session management."""

from __future__ import annotations

from datetime import datetime
from typing import Generator, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

_engine = None
SessionLocal: Optional[sessionmaker] = None


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    business_role = Column(String(255), nullable=True)
    system_role = Column(String(32), nullable=False, default="member")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Session(Base):
    """Authenticated user session."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Project(Base):
    """Team project workspace."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class ProjectMember(Base):
    """Project membership assignment."""

    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Note(Base):
    """Project note or update."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class NoteAttachment(Base):
    """Binary file attached to a note."""

    __tablename__ = "note_attachments"

    id = Column(Integer, primary_key=True)
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename = Column(String(36), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(255), nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)


def init_database(database_url: str) -> None:
    """Initialize SQLAlchemy engine and session factory."""
    global _engine, SessionLocal

    _engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_db_session() -> Generator[OrmSession, None, None]:
    """Yield a database session for request-scoped use."""
    if SessionLocal is None:
        raise RuntimeError("Database is not initialized. Call init_database() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
