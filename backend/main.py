
import logging
import time
from pathlib import Path
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from app.services.analytics import log_click
from app.services.url import get_url_for_redirect, mark_one_time_used, verify_url_password
from sqlalchemy.orm import Session

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import create_tables, engine, get_db
from app.schemas.url import RedirectPasswordRequest

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# Known SPA routes that should NOT be treated as short codes
KNOWN_SPA_ROUTES = {
    "login",
    "register",
    "dashboard",
    "analytics",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("smart-url-shortener")

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="Production-ready smart URL shortener with authentication, QR codes, analytics, admin tools, and reports.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Mount static frontend files if built
if FRONTEND_DIST.exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

request_buckets: dict[str, deque[float]] = defaultdict(deque)


def _serve_spa_index():
    """Safely serve the SPA index.html if present."""
    index_file = FRONTEND_DIST / "index.html"
    if FRONTEND_DIST.exists() and index_file.exists():
        return FileResponse(str(index_file))
    return None


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    started = time.perf_counter()
    client_ip = request.client.host if request.client else "unknown"
    bucket = request_buckets[client_ip]
    now = time.time()
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    bucket.append(now)
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info("%s %s %s %.2fms", request.method, request.url.path, response.status_code, elapsed_ms)
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.2f}"
    return response


@app.on_event("startup")
def on_startup() -> None:
    if settings.AUTO_CREATE_TABLES:
        try:
            create_tables()
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            logger.info("Database connected and tables are ready")
        except Exception as exc:  # noqa: BLE001 - never crash startup; Render kills the service
            logger.critical("Database startup step failed, but continuing app startup: %s", exc, exc_info=True)


@app.get("/")
def root():
    spa_response = _serve_spa_index()
    if spa_response is not None:
        return spa_response
    return {"message": "Welcome to Smart URL Shortener API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
    return {"status": "ok", "environment": settings.ENVIRONMENT}


def parse_client_context(request: Request) -> dict:
    user_agent = request.headers.get("user-agent", "")
    ua_lower = user_agent.lower()
    browser = "Chrome" if "chrome" in ua_lower else "Firefox" if "firefox" in ua_lower else "Safari" if "safari" in ua_lower else "Other"
    device = "Mobile" if any(token in ua_lower for token in ["mobile", "android", "iphone"]) else "Desktop"
    country = request.headers.get("cf-ipcountry") or request.headers.get("x-vercel-ip-country") or "Unknown"
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": user_agent,
        "referrer": request.headers.get("referer"),
        "country": country,
        "browser": browser,
        "device": device,
    }


def redirect_or_protected(url, request: Request, db: Session, password: str | None = None):
    if not verify_url_password(url, password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This URL is password protected")
    context = parse_client_context(request)
    log_click(db, url.id, **context)
    mark_one_time_used(db, url)
    return RedirectResponse(url.original_url)


@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Known SPA routes are not short codes — fall through to SPA
    if short_code in KNOWN_SPA_ROUTES:
        spa_response = _serve_spa_index()
        if spa_response is not None:
            return spa_response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    # Try to find a real short URL / custom alias
    url = get_url_for_redirect(db, short_code)
    if url:
        return redirect_or_protected(url, request, db)

    # If no short URL found, try to serve SPA (handles any new SPA routes too)
    spa_response = _serve_spa_index()
    if spa_response is not None:
        return spa_response

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="URL not found or expired"
    )


@app.post("/{short_code}/unlock")
def unlock_protected_url(
    short_code: str,
    payload: RedirectPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    url = get_url_for_redirect(db, short_code)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found or expired")
    return redirect_or_protected(url, request, db, payload.password)


@app.get("/{path:path}", include_in_schema=False)
async def spa_fallback(path: str):
    """Catch-all: serve SPA for any unmatched non-API GET routes."""
    if path.startswith("api/") or path.startswith("docs") or path.startswith("redoc") or path == "openapi.json" or path == "health":
        raise HTTPException(status_code=404, detail="Not found")
    spa_response = _serve_spa_index()
    if spa_response is not None:
        return spa_response
    raise HTTPException(status_code=404, detail="Not found")
