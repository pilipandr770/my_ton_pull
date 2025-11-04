#!/bin/bash
# Production startup wrapper - handles directory navigation for Render
# Simple approach: go to current directory, find and cd into backend

cd /opt/render/project/src 2>/dev/null || true

if [ -d "backend" ]; then
    cd backend
else
    # Fallback: search for it
    BACKEND_DIR=$(find / -type d -name backend 2>/dev/null | grep my_ton_pull | head -1)
    if [ -n "$BACKEND_DIR" ]; then
        cd "$BACKEND_DIR"
    else
        echo "ERROR: Could not find backend directory"
        exit 1
    fi
fi

echo "Starting gunicorn from: $(pwd)"
exec gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 1 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  app:app
