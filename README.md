# Smart URL Shortener & Analytics Platform

A production-ready full stack URL shortener built with React, Vite, FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication. The platform supports secure short links, custom aliases, QR code generation, password-protected URLs, one-time URLs, expiration, analytics, reports, profile management, and admin operations.

## Highlights

- JWT access and refresh token authentication
- PostgreSQL schema with constraints, foreign keys, indexes, and automatic table creation
- URL CRUD with custom aliases, expiration, password protection, and one-time links
- QR code SVG generation and download
- Click tracking with country, browser, device, and referrer analytics
- Dashboard, analytics, settings, admin panel, dark mode, responsive UI, CSV exports
- Docker, Docker Compose, Render, Railway, and Vercel deployment assets

## Tech Stack

- Frontend: React 18, Vite, Tailwind CSS, Axios, Chart.js
- Backend: FastAPI, SQLAlchemy, Pydantic, Passlib, python-jose
- Database: PostgreSQL
- Runtime target: Python 3.13 compatible, Node.js 18+

## Folder Structure

```text
Smart-URL-Shortener/
  backend/
    app/
      api/v1/
      core/
      models/
      schemas/
      services/
    main.py
    requirements.txt
    Dockerfile
  frontend/
    src/
      components/
      context/
      pages/
      services/
    package.json
    Dockerfile
  docs/
  diagrams/
  reports/
  docker-compose.yml
  README.md
```

## Local Setup

1. Create PostgreSQL database:

```bash
createdb smart_url_shortener_db
```

2. Configure backend environment:

```bash
cd backend
copy .env.example .env
```

Update `DATABASE_URL`, `SECRET_KEY`, `BACKEND_BASE_URL`, `FRONTEND_URL`, and `CORS_ORIGINS` in `backend/.env`.

3. Install backend dependencies and start API:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Swagger runs at `http://localhost:8000/docs`.

4. Install frontend dependencies and start Vite:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

## Core API

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `PUT /api/v1/auth/me`
- `POST /api/v1/urls/`
- `GET /api/v1/urls/`
- `PUT /api/v1/urls/{url_id}`
- `DELETE /api/v1/urls/{url_id}`
- `GET /api/v1/urls/{url_id}/qr`
- `GET /api/v1/analytics/stats`
- `GET /api/v1/analytics/report.csv`
- `GET /api/v1/admin/summary`

Full API notes are in [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

## Documentation

- [Installation Guide](docs/INSTALLATION_GUIDE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Project Report](reports/PROJECT_REPORT.md)
- [Resume and LinkedIn Copy](docs/PROJECT_DESCRIPTIONS.md)

## Verification

Validated locally:

- Backend imports and OpenAPI generation
- PostgreSQL health check
- Auth registration/login
- JWT-protected URL CRUD
- Analytics stats
- QR code generation
- Frontend production build

