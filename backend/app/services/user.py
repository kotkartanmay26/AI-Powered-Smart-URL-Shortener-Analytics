
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from app.core.config import settings
from sqlalchemy import or_

from app.models.user import RefreshToken, User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_admin=user.email.lower() in [email.lower() for email in settings.ADMIN_EMAILS],
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    identifier = email.strip()
    user = db.query(User).filter(or_(User.email == identifier, User.username == identifier)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user if user.is_active else None


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    data = user_update.model_dump(exclude_unset=True)
    if data.get("email") is not None:
        db_user.email = data["email"]
    if data.get("username") is not None:
        db_user.username = data["username"]
    if "full_name" in data:
        db_user.full_name = data["full_name"]
    if data.get("password"):
        db_user.hashed_password = get_password_hash(data["password"])
    db.commit()
    db.refresh(db_user)
    return db_user


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def store_refresh_token(db: Session, user_id: int, token: str) -> RefreshToken:
    db_token = RefreshToken(
        token_hash=hash_token(token),
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_valid_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    token_hash = hash_token(token)
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not db_token or db_token.revoked_at is not None:
        return None
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    return db_token


def revoke_refresh_token(db: Session, token: str) -> bool:
    db_token = get_valid_refresh_token(db, token)
    if not db_token:
        return False
    db_token.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return True
