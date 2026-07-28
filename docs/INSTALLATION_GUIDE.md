# Installation Guide

## Prerequisites

- Python 3.13
- Node.js 18 or newer
- PostgreSQL 14 or newer
- Git

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

Set these variables in `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/smart_url_shortener_db
SECRET_KEY=replace-with-a-long-random-secret
BACKEND_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Optional `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Common Windows Notes

If PowerShell blocks `npm`, run:

```bash
npm.cmd run dev
```

If a checked-in virtual environment points to an old Python path, delete `backend/venv` and recreate it.
