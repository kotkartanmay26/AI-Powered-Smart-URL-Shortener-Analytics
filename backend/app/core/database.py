
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings


def _normalize_db_url(url: str) -> str:
    """Normalize Render-style postgres:// URLs to sqlalchemy-compatible postgresql+psycopg2://."""
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


_NORMALIZED_DB_URL = _normalize_db_url(settings.DATABASE_URL)

# 1) Declare Base FIRST (so models can import it)
Base = declarative_base()

# 2) Import ALL models (they subclass Base, registering their tables in Base.metadata)
from app.models.user import User, RefreshToken  # noqa: F401,E402
from app.models.url import URL  # noqa: F401,E402
from app.models.click import Click  # noqa: F401,E402

# 3) Only NOW create the engine and sessionmaker (after metadata is populated)
engine = create_engine(
    _NORMALIZED_DB_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
    connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def create_tables() -> None:
    """Create all registered tables (checkfirst=True so existing are left alone)."""
    Base.metadata.create_all(bind=engine, checkfirst=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
