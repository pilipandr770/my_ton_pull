#!/usr/bin/env bash
# Unified build script - builds both backend and frontend
set -o errexit

echo "🔧 Building TON Pool - Unified Service"

# ============================================================================
# 1. BACKEND - Install Python dependencies
# ============================================================================
echo ""
echo "📦 Installing Python dependencies..."
cd backend
pip install --upgrade pip
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

engine = create_engine(database_url)
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
    conn.commit()
    print("✅ Schema 'ton_pool' created/verified")
END

# ============================================================================
# 3. FRONTEND - Install Node dependencies and build
# ============================================================================
echo ""
echo "📦 Installing Node.js dependencies..."
cd ../frontend
npm install

echo ""
echo "🏗️  Building Next.js frontend..."
npm run build

echo ""
echo "✅ Build completed successfully!"
echo "   - Backend: Python + Flask + PostgreSQL"
echo "   - Frontend: Next.js static export in frontend/out"
echo "   - Ready to start with gunicorn!"
