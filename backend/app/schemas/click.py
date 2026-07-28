
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClickBase(BaseModel):
    pass


class ClickCreate(ClickBase):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None
    browser: Optional[str] = None
    device: Optional[str] = None


class ClickResponse(ClickBase):
    id: int
    url_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None
    browser: Optional[str] = None
    device: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class URLWithClicks(BaseModel):
    id: int
    original_url: str
    short_code: str
    custom_alias: Optional[str] = None
    click_count: int
    is_active: bool
    expires_at: Optional[datetime] = None
    short_url: Optional[str] = None

    class Config:
        from_attributes = True


class DailyClickData(BaseModel):
    date: str
    clicks: int


class MonthlyClickData(BaseModel):
    month: str
    clicks: int


class AnalyticsStats(BaseModel):
    total_urls: int
    total_clicks: int
    active_links: int
    expired_links: int
    protected_links: int
    one_time_links: int
    top_urls: list[URLWithClicks]
    daily_clicks: list[DailyClickData]
    monthly_clicks: list[MonthlyClickData]
    countries: list[dict]
    browsers: list[dict]
    devices: list[dict]
    referrers: list[dict]
