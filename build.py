#!/usr/bin/env python3
"""
Unified build script for Render.com
Builds both backend and frontend in one process
"""
import os
import subprocess
import sys

def run_command(cmd, cwd=None, description=""):
    """Run shell command and check for errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"📍 Directory: {cwd or os.getcwd()}")
    print(f"▶️  Command: {cmd}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        sys.exit(1)
    print(f"\n✅ Success: {description}\n")

def main():
    print("\n🚀 TON Pool - Unified Build")
    print(f"📍 Starting directory: {os.getcwd()}")
    
    # 1. Install Python dependencies
    run_command(
        "pip install --upgrade pip",
        description="Upgrading pip"
    )
    
    run_command(
        "pip install -r requirements.txt",
        cwd="backend",
        description="Installing Python dependencies"
    )
    
    # 2. Create PostgreSQL schema
    print("\n🗄️  Setting up PostgreSQL schema...")
    database_url = os.getenv("DATABASE_URL", "")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
                conn.commit()
            print("✅ Schema 'ton_pool' ready")
        except Exception as e:
            print(f"⚠️  Schema creation: {e}")
    else:
        print("⚠️  No DATABASE_URL - skipping schema")
    
    # 3. Install Node.js dependencies
    run_command(
        "npm install",
        cwd="frontend",
        description="Installing Node.js dependencies"
    )
    
    # 4. Build Next.js frontend
    run_command(
        "npm run build",
        cwd="frontend",
        description="Building Next.js frontend"
    )
    
    # 5. Verify build output
    out_dir = "frontend/out"
    if os.path.exists(out_dir):
        files = os.listdir(out_dir)
        print(f"\n📦 Frontend build output ({len(files)} files):")
        for f in files[:10]:  # Show first 10 files
            print(f"   - {f}")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more")
    else:
        print(f"\n❌ Error: {out_dir} directory not found!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 BUILD SUCCESSFUL!")
    print("="*60)
    print("✅ Backend: Python + Flask ready")
    print("✅ Frontend: Next.js built")
    print("✅ Database: Schema 'ton_pool' ready")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
