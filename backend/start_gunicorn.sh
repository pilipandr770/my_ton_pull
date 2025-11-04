#!/bin/bash
# Production startup script for TON Staking Pool
# Handles proper directory setup and gunicorn startup

set -e

# Get the directory where this script is located (backend directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to backend directory
cd "$SCRIPT_DIR"

# Log startup info
echo "================================"
echo "🚀 TON Staking Pool Starting"
echo "================================"
echo "Script location: $SCRIPT_DIR"
echo "Working directory: $(pwd)"
echo "Python: $(python --version)"
echo "Gunicorn: $(gunicorn --version)"
echo "Port: ${PORT:-8000}"
echo "Workers: 1 (single worker)"
echo "================================"
echo ""

# Start gunicorn from the backend directory
exec gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 1 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  app:app
