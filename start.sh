
#!/usr/bin/env bash
set -euo pipefail

cd backend

PORT="${PORT:-10000}"
WORKERS="${WEB_CONCURRENCY:-2}"

echo "Starting server on port $PORT with $WORKERS workers..."

exec gunicorn main:app \
  --workers "$WORKERS" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:$PORT" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
