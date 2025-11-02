"""
Create superadmin user
Run this script once to create the initial admin account
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User


def create_superadmin(email, password):
    """Create or update superadmin user"""
    with app.app_context():
        # Ensure tables exist
        try:
            db.create_all()
            print("✅ Database tables ready")
        except Exception as e:
            print(f"⚠️  Database setup: {e}")
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"👤 User {email} already exists. Updating to admin...")
            user.role = 'admin'
            user.set_password(password)
            user.subscription_status = 'active'
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=3650)  # 10 years
            user.updated_at = datetime.utcnow()
        else:
            print(f"✨ Creating new superadmin: {email}")
            user = User(
                email=email,
                role='admin',
                subscription_status='active',
                subscription_expires_at=datetime.utcnow() + timedelta(days=3650)  # 10 years
            )
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ Superadmin {email} ready!")
        print(f"   Role: {user.role}")
        print(f"   Subscription: {user.subscription_status} until {user.subscription_expires_at}")
        return user


if __name__ == '__main__':
    # Create superadmin from environment or hardcoded values
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'pylypchukandrii770@gmail.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Dnepr75ok10')
    
    print("🔐 Creating superadmin account...")
    print(f"   Email: {ADMIN_EMAIL}")
    
    create_superadmin(ADMIN_EMAIL, ADMIN_PASSWORD)
