"""Admin panel routes."""

from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession

from auth import hash_password, require_admin
from database import Project, ProjectMember, User, get_db_session

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

SYSTEM_ROLES = ("admin", "coordinator", "member")


def _template_context(
    request: Request,
    current_user: User,
    **extra,
) -> dict:
    """Build common template context for admin pages."""
    return {
        "request": request,
        "current_user": current_user,
        "msg": request.query_params.get("msg"),
        "error": request.query_params.get("error"),
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


def _parse_deadline(value: str | None) -> datetime | None:
    """Parse HTML date input into a datetime."""
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d")


@router.get("/")
async def admin_index(
    request: Request,
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
):
    """Render admin panel home with section links."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    return templates.TemplateResponse(
        "admin/index.html",
        _template_context(request, current_user),
    )


@router.get("/users")
async def admin_users(
    request: Request,
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """List all users and show the create-user form."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/users.html",
        _template_context(request, current_user, users=users, system_roles=SYSTEM_ROLES),
    )


@router.post("/users")
async def admin_users_create(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(...),
    business_role: str = Form(""),
    system_role: str = Form(...),
    password: str = Form(...),
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Create a new user."""
    if isinstance(current_user, RedirectResponse):
        return current_user

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
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Render the user edit form."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "admin/user_form.html",
        _template_context(
            request,
            current_user,
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
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Update an existing user."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Toggle user active status."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    return _redirect("/admin/users", msg="user_toggled")


@router.post("/users/{user_id}/password")
async def admin_users_password(
    user_id: int,
    new_password: str = Form(...),
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Change a user's password."""
    if isinstance(current_user, RedirectResponse):
        return current_user

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
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """List all projects."""
    if isinstance(current_user, RedirectResponse):
        return current_user

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
    status: str = Form("active"),
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Create a new project."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    project = Project(
        title=title,
        description=description or None,
        deadline=_parse_deadline(deadline),
        status=status if status in ("active", "completed") else "active",
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    return _redirect("/admin/projects", msg="project_created")


@router.get("/projects/{project_id}/edit")
async def admin_projects_edit_form(
    project_id: int,
    request: Request,
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Render the project edit form."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return templates.TemplateResponse(
        "admin/project_form.html",
        _template_context(
            request,
            current_user,
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
    status: str = Form("active"),
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Update an existing project."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.title = title
    project.description = description or None
    project.deadline = _parse_deadline(deadline)
    project.status = status if status in ("active", "completed") else project.status
    project.updated_at = datetime.utcnow()
    db.commit()
    return _redirect("/admin/projects", msg="project_updated")


@router.post("/projects/{project_id}/toggle")
async def admin_projects_toggle(
    project_id: int,
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Toggle project status between active and completed."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = "completed" if project.status == "active" else "active"
    project.updated_at = datetime.utcnow()
    db.commit()
    return _redirect("/admin/projects", msg="project_toggled")


@router.get("/projects/{project_id}/members")
async def admin_project_members(
    project_id: int,
    request: Request,
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Manage project members."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    memberships = db.query(ProjectMember).filter_by(project_id=project_id).all()
    member_ids = {membership.user_id for membership in memberships}
    members = []
    for membership in memberships:
        user = db.query(User).filter_by(id=membership.user_id).first()
        if user:
            members.append({"user": user, "membership": membership})

    query = db.query(User).filter(User.is_active.is_(True))
    if member_ids:
        query = query.filter(User.id.notin_(member_ids))
    available_users = query.order_by(User.full_name).all()

    return templates.TemplateResponse(
        "admin/project_members.html",
        _template_context(
            request,
            current_user,
            project=project,
            members=members,
            available_users=available_users,
        ),
    )


@router.post("/projects/{project_id}/members")
async def admin_project_members_add(
    project_id: int,
    user_id: int = Form(...),
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Add a user to a project."""
    if isinstance(current_user, RedirectResponse):
        return current_user

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
    current_user: Union[User, RedirectResponse] = Depends(require_admin),
    db: DbSession = Depends(get_db_session),
):
    """Remove a user from a project."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    membership = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id, user_id=member_user_id)
        .first()
    )
    if membership:
        db.delete(membership)
        db.commit()

    return _redirect(f"/admin/projects/{project_id}/members", msg="member_removed")
