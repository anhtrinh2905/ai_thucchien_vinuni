#!/bin/sh
set -e

# Railway: shared Redis vars leak PORT=6379 — override for web server + healthcheck
if [ "$PORT" = "6379" ]; then
  echo "WARN: PORT=6379 is Redis port — switching to 8080"
  export PORT=8080
fi

PORT="${PORT:-8080}"
export PORT

# 1 worker = startup nhanh hơn, ổn định hơn trên Railway free tier
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers 1
