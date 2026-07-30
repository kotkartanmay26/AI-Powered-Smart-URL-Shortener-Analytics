
import logging
from typing import Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

logger = logging.getLogger(__name__)


def _normalize_db_url(url: str) -> str:
    """Normalize Render-style postgres:// URLs to sqlalchemy-compatible postgresql+psycopg2://."""
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _sanitize_db_url_for_log(url: str) -> str:
    """Return host:port/database from URL — NEVER log passwords."""
    try:
        # Drop the scheme first
        if "://" in url:
            _, body = url.split("://", 1)
        else:
            body = url
        # Drop user:password@ if present
        if "@" in body:
            _, body = body.rsplit("@", 1)
        return body.split("?")[0]
    except Exception:  # noqa: BLE001
        return "<unparseable-url>"


_NORMALIZED_DB_URL = _normalize_db_url(settings.DATABASE_URL)
_SANITIZED_DB_TARGET = _sanitize_db_url_for_log(_NORMALIZED_DB_URL)

# Log target host once at module load time so Render logs PROVE we are not
# using localhost in production. PASSWORD IS NEVER LOGGED.
logger.info(
    "SQLAlchemy target DB (host:port/db): %s  (localhost_used=%s)",
    _SANITIZED_DB_TARGET,
    "localhost" in _SANITIZED_DB_TARGET.lower(),
)

# 1) Declare Base FIRST. This file must FULLY finish importing before any
#    other module (e.g. app.models.*) imports Base from here. This is how we
#    avoid circular/partially-initialized-module errors.
Base = declarative_base()

# 2) DO NOT import app.models here at the top level! The models import Base
#    from this file, so a top-level reverse import would cause ImportError:
#    "cannot import name X from partially initialized module".

engine = create_engine(
    _NORMALIZED_DB_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
    connect_args={"connect_timeout": 10},
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
    """
    Create all tables. Models are imported ONLY HERE (inside a function, after
    this module is fully initialized) to break the circular import.

    Any error is caught and logged; this function never raises so that the
    application always starts and database errors can be inspected via /health.
    """
    from app.models.user import User, RefreshToken  # noqa: F401
    from app.models.url import URL  # noqa: F401
    from app.models.click import Click  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("create_tables() finished on %s", _SANITIZED_DB_TARGET)
    except Exception as exc:  # noqa: BLE001
        # Never propagate table-creation errors at startup. Let the app start.
        # Tables can be created later, and /health will surface DB issues.
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
