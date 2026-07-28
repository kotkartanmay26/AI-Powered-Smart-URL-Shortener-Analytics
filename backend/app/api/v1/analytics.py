
import csv
import io

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.schemas.click import AnalyticsStats, URLWithClicks
from app.services.analytics import get_analytics_stats, search_urls
from app.models.user import User

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/stats", response_model=AnalyticsStats)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_analytics_stats(db, current_user.id)


@router.get("/urls", response_model=list[URLWithClicks])
def list_urls_with_clicks(
    query: str = Query(None),
    is_active: bool = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return search_urls(db, current_user.id, query, is_active, page, size)


@router.get("/report.csv")
def export_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    urls = search_urls(db, current_user.id, size=10000)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["original_url", "short_url", "click_count", "is_active", "expires_at"])
    for url in urls:
        writer.writerow([url.original_url, url.short_url, url.click_count, url.is_active, url.expires_at])
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics-report.csv"},
    )
