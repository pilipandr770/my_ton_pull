#!/usr/bin/env bash
# Unified build script - builds both backend and frontend
set -o errexit

echo "🔧 Building TON Pool - Unified Service"
echo "📍 Current directory: $(pwd)"
echo "📂 Contents: $(ls -la)"

# ============================================================================
# 1. BACKEND - Install Python dependencies
# ============================================================================
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
cd backend
pip install -r requirements.txt

# ============================================================================
# 2. DATABASE - Create schema
# ============================================================================
echo ""
echo "🗄️  Setting up database..."
python << END
import os
from sqlalchemy import create_engine, text

database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if database_url:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
        conn.commit()
        print("✅ Schema 'ton_pool' created/verified")
else:
    print("⚠️  No DATABASE_URL - skipping schema creation")
END

# ============================================================================
# 3. FRONTEND - Install Node dependencies and build
# ============================================================================
echo ""
echo "📦 Installing Node.js dependencies..."
cd ../frontend
echo "📍 Now in: $(pwd)"

npm install

echo ""
echo "🏗️  Building Next.js frontend..."
npm run build

echo ""
echo "📂 Checking build output..."
ls -la out/ || echo "⚠️  out/ directory not found!"

echo ""
echo "✅ Build completed successfully!"
echo "   - Backend: Python + Flask + PostgreSQL"
echo "   - Frontend: Next.js static export"
echo "   - Frontend path: $(pwd)/out"
echo "   - Ready to start with gunicorn!"
