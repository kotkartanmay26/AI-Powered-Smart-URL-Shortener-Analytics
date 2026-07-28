
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import string
from datetime import datetime, timezone

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.url import URL
from app.schemas.url import URLCreate, URLUpdate
from app.models.user import User


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def add_short_url(url: URL) -> URL:
    code = url.custom_alias or url.short_code
    setattr(url, "short_url", f"{settings.BACKEND_BASE_URL.rstrip('/')}/{code}")
    return url


def get_url_by_short_code(db: Session, short_code: str) -> Optional[URL]:
    return db.query(URL).filter(URL.short_code == short_code).first()


def get_url_by_custom_alias(db: Session, custom_alias: str) -> Optional[URL]:
    return db.query(URL).filter(URL.custom_alias == custom_alias).first()


def get_url_by_id(db: Session, url_id: int) -> Optional[URL]:
    return db.query(URL).filter(URL.id == url_id).first()


def get_urls_by_user(
    db: Session,
    user_id: int,
    page: int = 1,
    size: int = 20,
    query: str | None = None,
    is_active: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[URL], int]:
    q = db.query(URL).filter(URL.user_id == user_id)
    if query:
        like = f"%{query}%"
        q = q.filter(or_(URL.original_url.ilike(like), URL.short_code.ilike(like), URL.custom_alias.ilike(like)))
    if is_active is not None:
        q = q.filter(URL.is_active == is_active)
    total = q.count()
    sort_column = getattr(URL, sort_by, URL.created_at)
    direction = desc if sort_order.lower() == "desc" else asc
    items = q.order_by(direction(sort_column)).offset((page - 1) * size).limit(size).all()
    return [add_short_url(item) for item in items], total


def create_url(db: Session, url: URLCreate, user: User) -> URL:
    # Check custom alias if provided
    if url.custom_alias:
        existing_alias = get_url_by_custom_alias(db, url.custom_alias)
        if existing_alias:
            raise ValueError("Custom alias already taken")

    # Generate unique short code
    short_code = generate_short_code()
    while get_url_by_short_code(db, short_code):
        short_code = generate_short_code()

    db_url = URL(
        original_url=str(url.original_url),
        short_code=short_code,
        custom_alias=url.custom_alias,
        title=url.title,
        description=url.description,
        password_hash=get_password_hash(url.password) if url.password else None,
        is_one_time=url.is_one_time,
        expires_at=url.expires_at,
        user_id=user.id
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return add_short_url(db_url)


def update_url(db: Session, url_id: int, url_update: URLUpdate, user: User) -> Optional[URL]:
    db_url = get_url_by_id(db, url_id)
    if not db_url or db_url.user_id != user.id:
        return None

    fields_set = url_update.model_fields_set

    if "original_url" in fields_set and url_update.original_url is not None:
        db_url.original_url = str(url_update.original_url)
    if "custom_alias" in fields_set:
        if url_update.custom_alias:
            existing_alias = get_url_by_custom_alias(db, url_update.custom_alias)
            if existing_alias and existing_alias.id != url_id:
                raise ValueError("Custom alias already taken")
        db_url.custom_alias = url_update.custom_alias
    if "title" in fields_set:
        db_url.title = url_update.title
    if "description" in fields_set:
        db_url.description = url_update.description
    if url_update.clear_password:
        db_url.password_hash = None
    elif url_update.password:
        db_url.password_hash = get_password_hash(url_update.password)
    if url_update.is_one_time is not None:
        db_url.is_one_time = url_update.is_one_time
        if not url_update.is_one_time:
            db_url.used_at = None
    if "expires_at" in fields_set:
        db_url.expires_at = url_update.expires_at
    if url_update.is_active is not None:
        db_url.is_active = url_update.is_active

    db.commit()
    db.refresh(db_url)
    return add_short_url(db_url)


def delete_url(db: Session, url_id: int, user: User) -> bool:
    db_url = get_url_by_id(db, url_id)
    if not db_url or db_url.user_id != user.id:
        return False
    db.delete(db_url)
    db.commit()
    return True


def get_url_for_redirect(db: Session, short_code: str) -> Optional[URL]:
    url = get_url_by_short_code(db, short_code)
    if not url:
        url = get_url_by_custom_alias(db, short_code)
    if not url:
        return None
    if not url.is_active:
        return None
    now = datetime.now(timezone.utc)
    expires_at = url.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at and now > expires_at:
        return None
    if url.is_one_time and url.used_at is not None:
        return None
    return url


def verify_url_password(url: URL, password: str | None) -> bool:
    if not url.password_hash:
        return True
    if not password:
        return False
    return verify_password(password, url.password_hash)


def mark_one_time_used(db: Session, url: URL) -> None:
    if url.is_one_time and url.used_at is None:
        url.used_at = datetime.now(timezone.utc)
        url.is_active = False
        db.commit()


def user_owns_url(url: URL | None, user: User) -> bool:
    return bool(url and (url.user_id == user.id or user.is_admin))
