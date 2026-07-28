
import csv
import io
from math import ceil

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.schemas.url import (
    BulkURLCreate,
    BulkURLResult,
    QRCodeResponse,
    URLCreate,
    URLListResponse,
    URLResponse,
    URLUpdate,
)
from app.services.url import (
    add_short_url,
    get_urls_by_user,
    get_url_by_id,
    create_url,
    update_url,
    delete_url,
    user_owns_url,
)
from app.models.user import User

router = APIRouter(prefix="/api/v1/urls", tags=["URLs"])


@router.get("/", response_model=URLListResponse)
def list_user_urls(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    query: str | None = Query(None, max_length=120),
    is_active: bool | None = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|original_url|short_code|is_active)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items, total = get_urls_by_user(db, current_user.id, page, size, query, is_active, sort_by, sort_order)
    return {"items": items, "total": total, "page": page, "size": size, "pages": ceil(total / size) if total else 0}


@router.get("/export/csv")
def export_urls_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, _ = get_urls_by_user(db, current_user.id, page=1, size=10000)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["id", "original_url", "short_url", "custom_alias", "is_active", "expires_at", "created_at"])
    for item in items:
        writer.writerow([item.id, item.original_url, item.short_url, item.custom_alias, item.is_active, item.expires_at, item.created_at])
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=urls-export.csv"},
    )


@router.get("/{url_id}", response_model=URLResponse)
def get_single_url(
    url_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    url = get_url_by_id(db, url_id)
    if not user_owns_url(url, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )
    return add_short_url(url)


@router.post("/", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
def create_new_url(
    url: URLCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return create_url(db, url, user=current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{url_id}", response_model=URLResponse)
def update_existing_url(
    url_id: int,
    url_update: URLUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        updated_url = update_url(db, url_id, url_update, user=current_user)
        if not updated_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found"
            )
        return updated_url
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_url(
    url_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_url(db, url_id, user=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )


@router.get("/{url_id}/qr", response_model=QRCodeResponse)
def get_url_qr(
    url_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = get_url_by_id(db, url_id)
    if not user_owns_url(url, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    add_short_url(url)
    img = qrcode.make(url.short_url, image_factory=qrcode.image.svg.SvgImage)
    stream = io.BytesIO()
    img.save(stream)
    return {"short_url": url.short_url, "qr_code_svg": stream.getvalue().decode("utf-8")}


@router.post("/bulk", response_model=BulkURLResult, status_code=status.HTTP_201_CREATED)
def bulk_create_urls(
    payload: BulkURLCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    created = []
    errors = []
    for index, item in enumerate(payload.urls):
        try:
            created.append(create_url(db, item, current_user))
        except ValueError as exc:
            errors.append({"index": index, "error": str(exc)})
    return {"created": created, "errors": errors}

