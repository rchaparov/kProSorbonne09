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
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

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

    user = relationship("User")


class ChecklistItem(Base):
    """Project checklist task item."""

    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    text = Column(String(1000), nullable=False)
    is_done = Column(Boolean, nullable=False, default=False)
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    creator = relationship("User", foreign_keys=[created_by])
    assignees = relationship(
        "ChecklistItemAssignee",
        cascade="all, delete-orphan",
        back_populates="item",
    )


class ChecklistItemAssignee(Base):
    """User assigned to a checklist item."""

    __tablename__ = "checklist_item_assignees"
    __table_args__ = (
        UniqueConstraint("item_id", "user_id", name="uq_checklist_assignees"),
    )

    id = Column(Integer, primary_key=True)
    item_id = Column(
        Integer,
        ForeignKey("checklist_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = relationship("User")
    item = relationship("ChecklistItem", back_populates="assignees")


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
    parent_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="SET NULL"),
        nullable=True,
    )
    quoted_content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    author = relationship("User", foreign_keys=[author_id])
    attachments = relationship(
        "NoteAttachment",
        cascade="all, delete-orphan",
        backref="note",
    )
    mentions = relationship(
        "NoteMention",
        cascade="all, delete-orphan",
        backref="note",
    )
    project = relationship("Project", backref="notes")
    material_links = relationship(
        "NoteMaterialLink",
        cascade="all, delete-orphan",
        backref="note",
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


class NoteMention(Base):
    """User mention in a project note."""

    __tablename__ = "note_mentions"

    id = Column(Integer, primary_key=True)
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = relationship("User")


class NoteMaterialLink(Base):
    """Link between a note and a knowledge base material."""

    __tablename__ = "note_material_links"
    __table_args__ = (
        UniqueConstraint("note_id", "material_id", name="uq_note_material_links_note_material"),
    )

    id = Column(Integer, primary_key=True)
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    material_id = Column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
    )

    material = relationship("Material")


class Notification(Base):
    """In-app notification for a user."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    note_id = Column(
        Integer,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=True,
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
    )
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


MATERIAL_CATEGORIES = ["Презентации", "Статьи", "Ссылки", "Видео", "Другое"]


class Material(Base):
    """Shared team knowledge base entry."""

    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="Другое")
    url = Column(String(2000), nullable=True)
    added_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    author = relationship("User", foreign_keys=[added_by])
    files = relationship(
        "MaterialFile",
        cascade="all, delete-orphan",
        backref="material",
    )


class MaterialFile(Base):
    """File attached to a knowledge base material."""

    __tablename__ = "material_files"

    id = Column(Integer, primary_key=True)
    material_id = Column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename = Column(String(36), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(255), nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TempFileToken(Base):
    """Short-lived public token for Office Online Viewer file access."""

    __tablename__ = "temp_file_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(36), unique=True, index=True, nullable=False)
    file_type = Column(String(20), nullable=False)
    file_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


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
