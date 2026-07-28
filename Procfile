
web: cd backend && gunicorn main:app --workers ${WEB_CONCURRENCY:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} --timeout 120
