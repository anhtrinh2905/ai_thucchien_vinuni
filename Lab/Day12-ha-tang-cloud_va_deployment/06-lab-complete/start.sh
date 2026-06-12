#!/bin/sh
set -e

# Railway: shared Redis vars leak PORT=6379 -> override for web server
if [ "$PORT" = "6379" ]; then
  echo "WARN: PORT=6379 is Redis port — switching to 8080"
  export PORT=8080
fi

PORT="${PORT:-8080}"
export PORT

exec streamlit run src/app.py \
  --server.address=0.0.0.0 \
  --server.port="$PORT" \
  --server.headless=true \
  --browser.gatherUsageStats=false
