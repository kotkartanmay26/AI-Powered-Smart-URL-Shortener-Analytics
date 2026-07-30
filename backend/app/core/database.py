
import logging
import os
from typing import Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

logger = logging.getLogger(__name__)


def _normalize_db_url(url: str) -> str:
    """Normalize Neon/Render-style URLs to sqlalchemy-compatible postgresql+psycopg2://.

    Handles:
      - postgres://         -> postgresql+psycopg2://
      - postgresql://       -> postgresql+psycopg2://
      - Already-suffixed    -> unchanged
    """
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _sanitize_db_url_for_log(url: str) -> str:
    """Return host:port/database from URL — NEVER log passwords."""
    try:
        if "://" in url:
            _, body = url.split("://", 1)
        else:
            body = url
        if "@" in body:
            _, body = body.rsplit("@", 1)
        return body.split("?")[0]
    except Exception:  # noqa: BLE001
        return "<unparseable-url>"


def _is_neon_host(url: str) -> bool:
    """Detect whether the URL points to a Neon PostgreSQL host."""
    return ".neon.tech" in url.lower()


def _build_connect_args(url: str) -> dict:
    """Build SQLAlchemy connect_args with Neon-compatible SSL settings.

    Neon managed PostgreSQL *requires* SSL. For local development (localhost)
    we allow non-SSL connections for convenience.
    """
    args = {"connect_timeout": 10}
    normalized = url.lower()
    is_localhost = (
        "localhost" in normalized
        or "127.0.0.1" in normalized
        or "0.0.0.0" in normalized
    )
    if _is_neon_host(url):
        args["sslmode"] = "require"
        logger.info("Neon host detected — enabling sslmode=require")
    elif "sslmode=require" in normalized or not is_localhost:
        if os.getenv("DB_SSL_REQUIRE", "1") == "1":
            args["sslmode"] = "require"
            logger.info("Remote/non-localhost DB — enabling sslmode=require (set DB_SSL_REQUIRE=0 to disable)")
    return args


_NORMALIZED_DB_URL = _normalize_db_url(settings.DATABASE_URL)
_SANITIZED_DB_TARGET = _sanitize_db_url_for_log(_NORMALIZED_DB_URL)
_CONNECT_ARGS = _build_connect_args(_NORMALIZED_DB_URL)

logger.info(
    "SQLAlchemy target DB (host:port/db): %s  (localhost_used=%s, neon_host=%s)",
    _SANITIZED_DB_TARGET,
    "localhost" in _SANITIZED_DB_TARGET.lower(),
    _is_neon_host(_NORMALIZED_DB_URL),
)

Base = declarative_base()

engine = create_engine(
    _NORMALIZED_DB_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    future=True,
    connect_args=_CONNECT_ARGS,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def check_db_connectivity() -> Tuple[bool, str]:
    """Run a simple SELECT 1 check. Returns (ok, message)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, f"OK -> {_SANITIZED_DB_TARGET}"
    except Exception as exc:  # noqa: BLE001
        return False, f"FAIL -> {_SANITIZED_DB_TARGET} : {exc.__class__.__name__}: {exc}"


def create_tables() -> None:
    from app.models.user import User, RefreshToken  # noqa: F401
    from app.models.url import URL  # noqa: F401
    from app.models.click import Click  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("create_tables() finished on %s", _SANITIZED_DB_TARGET)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "create_tables() skipped (non-fatal) on %s : %s",
            _SANITIZED_DB_TARGET,
            exc,
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
