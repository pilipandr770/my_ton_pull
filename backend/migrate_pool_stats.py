# backend/migrate_pool_stats.py
"""
Migrate pool_stats table - add missing columns
Run this once on Render Shell
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")

# Add SSL mode for Render PostgreSQL
if "sslmode" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL += f"{separator}sslmode=require"

print("🔧 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

try:
    print("📋 Checking ton_pool.pool_stats table...")
    
    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'ton_pool' 
            AND table_name = 'pool_stats'
        )
    """)
    table_exists = cur.fetchone()[0]
    
    if not table_exists:
        print("❌ Table ton_pool.pool_stats does not exist")
        print("✨ Creating table...")
        cur.execute("""
            CREATE TABLE ton_pool.pool_stats (
                id SERIAL PRIMARY KEY,
                total_pool_ton DOUBLE PRECISION DEFAULT 0.0,
                total_jettons DOUBLE PRECISION DEFAULT 0.0,
                apy DOUBLE PRECISION DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Table created!")
    else:
        print("✅ Table exists, checking columns...")
        
        # Add columns if missing
        columns_to_add = [
            ("total_pool_ton", "DOUBLE PRECISION DEFAULT 0.0"),
            ("total_jettons", "DOUBLE PRECISION DEFAULT 0.0"),
            ("apy", "DOUBLE PRECISION DEFAULT 0.0"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cur.execute(f"""
                    ALTER TABLE ton_pool.pool_stats 
                    ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                """)
                print(f"✅ Column {col_name} added/verified")
            except Exception as e:
                print(f"⚠️  Column {col_name}: {e}")
    
    # Insert initial data if table is empty
    cur.execute("SELECT COUNT(*) FROM ton_pool.pool_stats")
    count = cur.fetchone()[0]
    
    if count == 0:
        print("📊 Inserting initial pool stats...")
        cur.execute("""
            INSERT INTO ton_pool.pool_stats (total_pool_ton, total_jettons, apy, updated_at)
            VALUES (12345.678, 98765.432, 0.097, CURRENT_TIMESTAMP)
        """)
        print("✅ Initial data inserted!")
    
    conn.commit()
    print("\n✅ Migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Error: {e}")
    raise
finally:
    cur.close()
    conn.close()
