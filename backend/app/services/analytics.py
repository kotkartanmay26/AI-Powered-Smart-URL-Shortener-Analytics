
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func, or_
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.click import Click
from app.models.url import URL
from app.schemas.click import URLWithClicks, DailyClickData, MonthlyClickData


def log_click(
    db: Session,
    url_id: int,
    ip_address: str = None,
    user_agent: str = None,
    referrer: str = None,
    country: str = None,
    browser: str = None,
    device: str = None,
):
    click = Click(
        url_id=url_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
        country=country,
        browser=browser,
        device=device,
    )
    db.add(click)
    db.commit()
    db.refresh(click)
    return click


def get_analytics_stats(db: Session, user_id: int):
    # Total URLs
    total_urls = db.query(func.count(URL.id)).filter(URL.user_id == user_id).scalar() or 0

    # Total Clicks (count all clicks on user's URLs)
    total_clicks = db.query(func.count(Click.id)).join(URL).filter(URL.user_id == user_id).scalar() or 0

    # Active Links
    active_links = db.query(func.count(URL.id)).filter(
        and_(URL.user_id == user_id, URL.is_active == True)
    ).scalar() or 0

    # Expired Links
    now = datetime.now(timezone.utc)
    expired_links = db.query(func.count(URL.id)).filter(
        and_(
            URL.user_id == user_id,
            URL.expires_at.isnot(None),
            URL.expires_at < now
        )
    ).scalar() or 0

    protected_links = db.query(func.count(URL.id)).filter(
        and_(URL.user_id == user_id, URL.password_hash.isnot(None))
    ).scalar() or 0

    one_time_links = db.query(func.count(URL.id)).filter(
        and_(URL.user_id == user_id, URL.is_one_time == True)
    ).scalar() or 0

    # Top URLs (sorted by click count)
    top_urls = db.query(
        URL,
        func.count(Click.id).label('click_count')
    ).outerjoin(Click).filter(URL.user_id == user_id)\
     .group_by(URL.id)\
     .order_by(func.count(Click.id).desc())\
     .limit(10).all()

    top_urls_list = []
    for url_obj, count in top_urls:
        top_urls_list.append(
            URLWithClicks(
                id=url_obj.id,
                original_url=url_obj.original_url,
                short_code=url_obj.short_code,
                custom_alias=url_obj.custom_alias,
                click_count=count,
                is_active=url_obj.is_active,
                expires_at=url_obj.expires_at,
                short_url=f"{settings.BACKEND_BASE_URL.rstrip('/')}/{url_obj.custom_alias or url_obj.short_code}",
            )
        )

    # Daily Clicks (last 30 days)
    daily_clicks = []
    for i in range(29, -1, -1):
        date = now - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        next_date = date + timedelta(days=1)
        count = db.query(func.count(Click.id))\
                  .join(URL)\
                  .filter(
                      URL.user_id == user_id,
                      Click.created_at >= date,
                      Click.created_at < next_date
                  ).scalar() or 0
        daily_clicks.append(DailyClickData(date=date_str, clicks=count))

    # Monthly Clicks (last 12 months)
    monthly_clicks = []
    for i in range(11, -1, -1):
        year = now.year if (now.month - i > 0) else now.year - 1
        month = (now.month - i) % 12
        if month == 0:
            month = 12
        month_str = f"{year}-{month:02d}"
        count = db.query(func.count(Click.id))\
                  .join(URL)\
                  .filter(
                      URL.user_id == user_id,
                      extract('year', Click.created_at) == year,
                      extract('month', Click.created_at) == month
                  ).scalar() or 0
        monthly_clicks.append(MonthlyClickData(month=month_str, clicks=count))

    def grouped(column, limit=8):
        rows = (
            db.query(column.label("name"), func.count(Click.id).label("value"))
            .join(URL)
            .filter(URL.user_id == user_id, column.isnot(None))
            .group_by(column)
            .order_by(func.count(Click.id).desc())
            .limit(limit)
            .all()
        )
        return [{"name": name or "Unknown", "value": int(value or 0)} for name, value in rows]

    return {
        "total_urls": total_urls,
        "total_clicks": total_clicks,
        "active_links": active_links,
        "expired_links": expired_links,
        "protected_links": protected_links,
        "one_time_links": one_time_links,
        "top_urls": top_urls_list,
        "daily_clicks": daily_clicks,
        "monthly_clicks": monthly_clicks,
        "countries": grouped(Click.country),
        "browsers": grouped(Click.browser),
        "devices": grouped(Click.device),
        "referrers": grouped(Click.referrer),
    }


def search_urls(
    db: Session,
    user_id: int,
    query: str = None,
    is_active: bool = None,
    page: int = 1,
    size: int = 20,
):
    q = db.query(URL, func.count(Click.id).label('click_count'))\
          .outerjoin(Click)\
          .filter(URL.user_id == user_id)

    if query:
        q = q.filter(
            or_(
                URL.original_url.ilike(f"%{query}%"),
                URL.short_code.ilike(f"%{query}%"),
                URL.custom_alias.ilike(f"%{query}%"),
            )
        )

    if is_active is not None:
        q = q.filter(URL.is_active == is_active)

    results = q.group_by(URL.id).order_by(func.count(Click.id).desc()).offset((page - 1) * size).limit(size).all()

    url_list = []
    for url_obj, count in results:
        url_list.append(
            URLWithClicks(
                id=url_obj.id,
                original_url=url_obj.original_url,
                short_code=url_obj.short_code,
                custom_alias=url_obj.custom_alias,
                click_count=count,
                is_active=url_obj.is_active,
                expires_at=url_obj.expires_at,
                short_url=f"{settings.BACKEND_BASE_URL.rstrip('/')}/{url_obj.custom_alias or url_obj.short_code}",
            )
        )

    return url_list
