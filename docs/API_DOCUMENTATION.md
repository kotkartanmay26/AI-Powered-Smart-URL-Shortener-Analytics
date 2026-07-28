# API Documentation

Base URL: `http://localhost:8000`

Swagger UI: `/docs`

## Authentication

### Register

`POST /api/v1/auth/register`

```json
{
  "email": "user@example.com",
  "username": "user123",
  "full_name": "User Name",
  "password": "StrongPass123"
}
```

### Login

`POST /api/v1/auth/login`

Returns `access_token`, `refresh_token`, and `token_type`.

### Refresh

`POST /api/v1/auth/refresh`

```json
{ "refresh_token": "..." }
```

### Profile

- `GET /api/v1/auth/me`
- `PUT /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/forgot-password`

## URLs

### Create URL

`POST /api/v1/urls/`

```json
{
  "original_url": "https://example.com",
  "custom_alias": "example",
  "title": "Example campaign",
  "description": "Optional notes",
  "password": "1234",
  "is_one_time": false,
  "expires_at": "2026-12-31T23:59:00"
}
```

### List URLs

`GET /api/v1/urls/?page=1&size=20&query=demo&is_active=true&sort_by=created_at&sort_order=desc`

### Update URL

`PUT /api/v1/urls/{url_id}`

### Delete URL

`DELETE /api/v1/urls/{url_id}`

### QR Code

`GET /api/v1/urls/{url_id}/qr`

Returns SVG content and the short URL.

### Bulk Create

`POST /api/v1/urls/bulk`

```json
{
  "urls": [
    { "original_url": "https://example.com/a" },
    { "original_url": "https://example.com/b", "custom_alias": "demo-b" }
  ]
}
```

### Export

`GET /api/v1/urls/export/csv`

## Redirects

- `GET /{short_code}`
- `POST /{short_code}/unlock` for password-protected redirects

## Analytics

- `GET /api/v1/analytics/stats`
- `GET /api/v1/analytics/urls`
- `GET /api/v1/analytics/report.csv`

Analytics includes totals, daily/monthly clicks, top URLs, countries, browsers, devices, and referrers.

## Admin

Admin access requires `is_admin=true`. Add admin emails through `ADMIN_EMAILS` before registration.

- `GET /api/v1/admin/summary`
- `GET /api/v1/admin/users`
- `PATCH /api/v1/admin/users/{user_id}/status?is_active=false`
- `DELETE /api/v1/admin/urls/{url_id}`
