#!/usr/bin/env bash
# build.sh - Build script for Render.com deployment
# Automatically runs database migrations on deployment

set -o errexit  # Exit on error

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️  Setting up database..."

# Create ton_pool schema if it doesn't exist
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

echo "🔄 Initializing Flask-Migrate..."
export FLASK_APP=app.py

# Initialize migrations if not exists
if [ ! -d "migrations" ]; then
    echo "📦 Creating migrations directory..."
    flask db init
fi

echo "🔄 Generating migration..."
flask db migrate -m "Auto-migration on deployment"

echo "⬆️  Running database migrations..."
flask db upgrade

echo "✅ Build completed successfully!"
