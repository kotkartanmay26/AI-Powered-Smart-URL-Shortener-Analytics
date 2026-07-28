
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class URLBase(BaseModel):
    original_url: HttpUrl


class URLCreate(URLBase):
    custom_alias: Optional[str] = Field(default=None, min_length=3, max_length=60, pattern=r"^[a-zA-Z0-9_-]+$")
    title: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    password: Optional[str] = Field(default=None, min_length=4, max_length=128)
    is_one_time: bool = False
    expires_at: Optional[datetime] = None


class URLUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    custom_alias: Optional[str] = Field(default=None, min_length=3, max_length=60, pattern=r"^[a-zA-Z0-9_-]+$")
    title: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    password: Optional[str] = Field(default=None, min_length=4, max_length=128)
    clear_password: bool = False
    is_one_time: Optional[bool] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class URLResponse(URLBase):
    id: int
    short_code: str
    custom_alias: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_password_protected: bool = False
    is_one_time: bool
    used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    short_url: str | None = None

    class Config:
        from_attributes = True


class URLListResponse(BaseModel):
    items: list[URLResponse]
    total: int
    page: int
    size: int
    pages: int


class RedirectPasswordRequest(BaseModel):
    password: str


class QRCodeResponse(BaseModel):
    short_url: str
    qr_code_svg: str


class BulkURLCreate(BaseModel):
    urls: list[URLCreate] = Field(min_length=1, max_length=100)


class BulkURLResult(BaseModel):
    created: list[URLResponse]
    errors: list[dict]
