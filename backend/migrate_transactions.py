# backend/migrate_transactions.py
"""
Migrate transactions table - add missing 'type' column
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
    print("📋 Checking ton_pool.transactions table...")

    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'ton_pool'
            AND table_name = 'transactions'
        )
    """)
    table_exists = cur.fetchone()[0]

    if not table_exists:
        print("❌ Table ton_pool.transactions does not exist")
        print("⚠️  This script is for adding missing columns to existing table")
        print("   If table doesn't exist, it will be created by the app on first run")
    else:
        print("✅ Table exists, checking columns...")

        # Check if 'type' column exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'ton_pool'
                AND table_name = 'transactions'
                AND column_name = 'type'
            )
        """)
        type_exists = cur.fetchone()[0]

        if type_exists:
            print("✅ Column 'type' already exists")
        else:
            print("❌ Column 'type' missing, adding it...")
            try:
                cur.execute("""
                    ALTER TABLE ton_pool.transactions
                    ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'stake'
                """)
                print("✅ Column 'type' added successfully!")
            except Exception as e:
                print(f"❌ Error adding column: {e}")
                raise

    conn.commit()
    print("\n✅ Migration completed successfully!")

except Exception as e:
    conn.rollback()
    print(f"\n❌ Error: {e}")
    raise
finally:
    cur.close()
    conn.close()