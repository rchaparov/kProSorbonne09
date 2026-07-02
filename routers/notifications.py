"""In-app notification routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DbSession

from auth import get_current_user, get_unread_count
from database import Notification, get_db_session
from main import templates
from utils.nav import nav_context

router = APIRouter(tags=["notifications"])


@router.get("/notifications")
async def notifications_page(
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the user's notification list."""
    notifications = (
        db.query(Notification)
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "notifications.html",
        {
            "request": request,
            "current_user": current_user,
            "notifications": notifications,
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db),
        },
    )


@router.post("/notifications/read-all")
async def read_all_notifications(
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Mark all notifications as read for the current user."""
    db.query(Notification).filter_by(user_id=current_user.id, is_read=False).update(
        {"is_read": True}
    )
    db.commit()
    return RedirectResponse("/notifications", status_code=303)


@router.post("/notifications/{notification_id}/read")
async def read_one_notification(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Mark one notification as read and redirect to the related project."""
    notification = (
        db.query(Notification)
        .filter_by(id=notification_id, user_id=current_user.id)
        .first()
    )
    if notification:
        notification.is_read = True
        db.commit()
        if notification.project_id:
            return RedirectResponse(
                f"/projects/{notification.project_id}",
                status_code=303,
            )

    return RedirectResponse("/notifications", status_code=303)
