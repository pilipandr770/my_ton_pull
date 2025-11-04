# backend/models.py
"""
Database models for TON Staking Pool
Uses separate schema 'ton_pool' for multi-project PostgreSQL database
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def _schema():
    # використай схему тільки для Postgres; для SQLite schema ігнорується
    return {'schema': 'ton_pool'}

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = _schema()
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default='user')  # 'user' | 'admin'
    subscription_status = db.Column(db.String(20), default='inactive')  # 'inactive'|'active'|'trial'
    subscription_expires_at = db.Column(db.DateTime, nullable=True)

    wallet_address = db.Column(db.String(128), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pwd: str):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.password_hash, pwd)

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'role': self.role,
            'subscription_status': self.subscription_status,
            'subscription_expires_at': self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
            'wallet_address': self.wallet_address,
            'created_at': self.created_at.isoformat()
        }
        if include_email:
            data['email'] = self.email
        return data

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    __table_args__ = _schema()
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(f"ton_pool.users.id"), nullable=False, index=True)

    stripe_customer_id = db.Column(db.String(80), nullable=True, index=True)
    stripe_subscription_id = db.Column(db.String(80), nullable=True, unique=True, index=True)
    status = db.Column(db.String(20), default='inactive')  # 'active','canceled','past_due'
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='subscriptions')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stripe_customer_id': self.stripe_customer_id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'created_at': self.created_at.isoformat()
        }

class PoolStats(db.Model):
    __tablename__ = 'pool_stats'
    __table_args__ = _schema()
    id = db.Column(db.Integer, primary_key=True)
    total_pool_ton = db.Column(db.Float, default=0.0)
    total_jettons = db.Column(db.Float, default=0.0)
    apy = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'total_pool_ton': self.total_pool_ton,
            'total_jettons': self.total_jettons,
            'apy': self.apy,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = _schema()
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(f"ton_pool.users.id"), nullable=True, index=True)
    tx_hash = db.Column(db.String(200), nullable=False, unique=True, index=True)
    type = db.Column(db.String(20), nullable=False)  # 'stake' | 'unstake'
    amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # 'pending' | 'confirmed' | 'failed'
    direction = db.Column(db.String(10), nullable=True)  # DEPRECATED: use 'type' instead
    amount_ton = db.Column(db.Float, default=0.0)  # DEPRECATED: use 'amount' instead
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='transactions')

    def update_status(self, new_status: str):
        """Update transaction status and timestamp"""
        if new_status in ['pending', 'confirmed', 'failed']:
            self.status = new_status
            self.updated_at = datetime.utcnow()
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tx_hash': self.tx_hash,
            'type': self.type,
            'amount': self.amount,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
