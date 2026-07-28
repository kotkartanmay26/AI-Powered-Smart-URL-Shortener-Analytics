# Deployment Guide

## Docker Compose

```bash
docker compose up --build
```

## Render

1. Push the repository to GitHub.
2. Create a PostgreSQL database on Render.
3. Create a Docker web service from `backend/Dockerfile`.
4. Set environment variables:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `BACKEND_BASE_URL`
   - `FRONTEND_URL`
   - `CORS_ORIGINS`
   - `AUTO_CREATE_TABLES=true`
5. Deploy the frontend to Vercel and update CORS with the Vercel URL.

## Railway

1. Create a Railway project.
2. Add PostgreSQL.
3. Deploy the backend using `railway.json`.
4. Set the same backend environment variables.

## Vercel

1. Import the `frontend` directory.
2. Set `VITE_API_BASE_URL` to the deployed backend URL.
3. Deploy.

## Production Checklist

- Rotate `SECRET_KEY`.
- Use a managed PostgreSQL instance.
- Restrict `CORS_ORIGINS` to deployed frontend domains.
- Set `ADMIN_EMAILS` before creating admin accounts.
- Disable debug mode.
- Use HTTPS for frontend and backend.
- Add external email provider for password reset delivery.
