from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.click import Click
from app.models.url import URL
from app.models.user import User
from app.schemas.user import MessageResponse, UserResponse

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


@router.get("/summary")
def admin_summary(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "urls": db.query(func.count(URL.id)).scalar() or 0,
        "clicks": db.query(func.count(Click.id)).scalar() or 0,
        "active_urls": db.query(func.count(URL.id)).filter(URL.is_active == True).scalar() or 0,
    }


@router.get("/users", response_model=list[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()


@router.patch("/users/{user_id}/status", response_model=UserResponse)
def set_user_status(
    user_id: int,
    is_active: bool,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/urls/{url_id}", response_model=MessageResponse)
def admin_delete_url(
    url_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    url = db.query(URL).filter(URL.id == url_id).first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    db.delete(url)
    db.commit()
    return {"message": "URL deleted"}
