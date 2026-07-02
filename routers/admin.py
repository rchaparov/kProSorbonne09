"""Admin panel routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import get_unread_count, hash_password, require_admin
from database import Project, ProjectMember, User, get_db_session
from limiter import limiter
from main import templates
from utils.date_utils import parse_deadline
from utils.nav import nav_context
from utils.progress import PROJECT_STATUSES, PROJECT_STATUS_COLORS, PROJECT_STATUS_LABELS

router = APIRouter(prefix="/admin", tags=["admin"])

SYSTEM_ROLES = ("admin", "coordinator", "member")


def _template_context(
    request: Request,
    current_user: User,
    db: DbSession | None = None,
    current_project_id: int | None = None,
    **extra,
) -> dict:
    """Build common template context for admin pages."""
    unread_count = 0
    nav = {"recent_projects": [], "current_project_id": current_project_id}
    if db is not None:
        unread_count = get_unread_count(current_user, db)
        nav = nav_context(current_user, db, current_project_id)
    return {
        "request": request,
        "current_user": current_user,
        "msg": request.query_params.get("msg"),
        "error": request.query_params.get("error"),
        "unread_count": unread_count,
        "status_labels": PROJECT_STATUS_LABELS,
        "status_colors": PROJECT_STATUS_COLORS,
        **nav,
        **extra,
    }


def _redirect(path: str, msg: str | None = None, error: str | None = None) -> RedirectResponse:
    """Redirect with optional flash query parameters."""
    params: list[str] = []
    if msg:
        params.append(f"msg={msg}")
    if error:
        params.append(f"error={error}")
    url = path
    if params:
        url = f"{path}?{'&'.join(params)}"
    return RedirectResponse(url, status_code=303)


@router.get("/")
async def admin_index(
    request: Request,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Render admin panel home with section links."""
    return templates.TemplateResponse(
        "admin/index.html",
        _template_context(request, current_user, db=db),
    )


@router.get("/users")
async def admin_users(
    request: Request,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """List all users and show the create-user form."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/users.html",
        _template_context(request, current_user, db=db, users=users, system_roles=SYSTEM_ROLES),
    )


@router.post("/users")
async def admin_users_create(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(...),
    business_role: str = Form(""),
    system_role: str = Form(...),
    password: str = Form(...),
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Create a new user."""
    username = username.strip()
    full_name = full_name.strip()
    business_role = business_role.strip()

    if len(password) < 6:
        return _redirect("/admin/users", error="password_short")

    if db.query(User).filter_by(username=username).first():
        return _redirect("/admin/users", error="username_exists")

    if system_role not in SYSTEM_ROLES:
        raise HTTPException(status_code=400, detail="Invalid system role")

    user = User(
        username=username,
        full_name=full_name,
        business_role=business_role or None,
        system_role=system_role,
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    return _redirect("/admin/users", msg="user_created")


@router.get("/users/{user_id}/edit")
async def admin_users_edit_form(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Render the user edit form."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "admin/user_form.html",
        _template_context(
            request,
            current_user,
            db=db,
            user=user,
            system_roles=SYSTEM_ROLES,
            form_action=f"/admin/users/{user_id}/edit",
        ),
    )


@router.post("/users/{user_id}/edit")
async def admin_users_edit(
    user_id: int,
    request: Request,
    username: str = Form(...),
    full_name: str = Form(...),
    business_role: str = Form(""),
    system_role: str = Form(...),
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Update an existing user."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    username = username.strip()
    full_name = full_name.strip()
    business_role = business_role.strip()

    existing = db.query(User).filter_by(username=username).first()
    if existing and existing.id != user_id:
        return _redirect(f"/admin/users/{user_id}/edit", error="username_exists")

    if system_role not in SYSTEM_ROLES:
        raise HTTPException(status_code=400, detail="Invalid system role")

    user.username = username
    user.full_name = full_name
    user.business_role = business_role or None
    user.system_role = system_role
    db.commit()
    return _redirect("/admin/users", msg="user_updated")


@router.post("/users/{user_id}/toggle")
async def admin_users_toggle(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Toggle user active status."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    return _redirect("/admin/users", msg="user_toggled")


@router.post("/users/{user_id}/password")
@limiter.limit("5/minute")
async def admin_users_password(
    user_id: int,
    request: Request,
    new_password: str = Form(...),
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Change a user's password."""
    if len(new_password) < 6:
        return _redirect("/admin/users", error="password_short")

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(new_password)
    db.commit()
    return _redirect("/admin/users", msg="password_changed")


@router.get("/projects")
async def admin_projects(
    request: Request,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """List all projects."""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    member_counts = dict(
        db.query(ProjectMember.project_id, func.count(ProjectMember.id))
        .group_by(ProjectMember.project_id)
        .all()
    )
    return templates.TemplateResponse(
        "admin/projects.html",
        _template_context(
            request,
            current_user,
            db=db,
            projects=projects,
            member_counts=member_counts,
        ),
    )


@router.post("/projects")
async def admin_projects_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(""),
    status: str = Form("planning"),
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Create a new project."""
    project = Project(
        title=title,
        description=description or None,
        deadline=parse_deadline(deadline),
        status=status if status in PROJECT_STATUSES else "planning",
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    return _redirect("/admin/projects", msg="project_created")


@router.get("/projects/{project_id}/edit")
async def admin_projects_edit_form(
    project_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Render the project edit form."""
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return templates.TemplateResponse(
        "admin/project_form.html",
        _template_context(
            request,
            current_user,
            db=db,
            current_project_id=project_id,
            project=project,
            form_action=f"/admin/projects/{project_id}/edit",
        ),
    )


@router.post("/projects/{project_id}/edit")
async def admin_projects_edit(
    project_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(""),
    status: str = Form("planning"),
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Update an existing project."""
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.title = title
    project.description = description or None
    project.deadline = parse_deadline(deadline)
    project.status = status if status in PROJECT_STATUSES else project.status
    project.updated_at = datetime.utcnow()
    db.commit()
    return _redirect("/admin/projects", msg="project_updated")


@router.post("/projects/{project_id}/toggle")
async def admin_projects_toggle(
    project_id: int,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Toggle project status between active and completed."""
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status == "active":
        project.status = "completed"
    elif project.status == "completed":
        project.status = "active"
    else:
        return _redirect("/admin/projects", error="invalid_toggle")

    project.updated_at = datetime.utcnow()
    db.commit()
    return _redirect("/admin/projects", msg="project_toggled")


@router.get("/projects/{project_id}/members")
async def admin_project_members(
    project_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Manage project members."""
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    memberships = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id)
        .options(joinedload(ProjectMember.user))
        .all()
    )
    member_ids = {membership.user_id for membership in memberships}
    members = [
        {"user": membership.user, "membership": membership}
        for membership in memberships
        if membership.user
    ]

    query = db.query(User).filter(User.is_active.is_(True))
    if member_ids:
        query = query.filter(User.id.notin_(member_ids))
    available_users = query.order_by(User.full_name).all()

    return templates.TemplateResponse(
        "admin/project_members.html",
        _template_context(
            request,
            current_user,
            db=db,
            current_project_id=project_id,
            project=project,
            members=members,
            available_users=available_users,
        ),
    )


@router.post("/projects/{project_id}/members")
async def admin_project_members_add(
    project_id: int,
    user_id: int = Form(...),
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Add a user to a project."""
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user = db.query(User).filter_by(id=user_id, is_active=True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id, user_id=user_id)
        .first()
    )
    if not existing:
        db.add(ProjectMember(project_id=project_id, user_id=user_id))
        db.commit()

    return _redirect(f"/admin/projects/{project_id}/members", msg="member_added")


@router.post("/projects/{project_id}/members/{member_user_id}/remove")
async def admin_project_members_remove(
    project_id: int,
    member_user_id: int,
    current_user: User = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Remove a user from a project."""
    membership = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id, user_id=member_user_id)
        .first()
    )
    if membership:
        db.delete(membership)
        db.commit()

    return _redirect(f"/admin/projects/{project_id}/members", msg="member_removed")
