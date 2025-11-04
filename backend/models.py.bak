"""
Database models for TON Staking Pool
Uses separate schema 'ton_pool' for multi-project PostgreSQL database
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User accounts in the staking pool"""
    __tablename__ = 'users'
    __table_args__ = {'schema': 'ton_pool'}
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role and subscription
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    subscription_status = db.Column(db.String(20), default='inactive')  # 'inactive', 'active', 'trial'
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    
    # TON wallet (optional for users who want to stake)
    wallet_address = db.Column(db.String(100), unique=True, nullable=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    transactions = db.relationship('Transaction', back_populates='user', lazy='dynamic')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def has_active_subscription(self):
        """Check if user has active subscription"""
        if self.subscription_status == 'active' and self.subscription_expires_at:
            return self.subscription_expires_at > datetime.utcnow()
        return False
    
    def to_dict(self, include_email=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'wallet_address': self.wallet_address,
            'role': self.role,
            'subscription_status': self.subscription_status,
            'subscription_expires_at': self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
            'created_at': self.created_at.isoformat()
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'


class Transaction(db.Model):
    """Transaction history for deposits and withdrawals"""
    __tablename__ = 'transactions'
    __table_args__ = {'schema': 'ton_pool'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ton_pool.users.id'), nullable=False)
    
    tx_hash = db.Column(db.String(100), unique=True, nullable=False, index=True)
    tx_type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'withdraw'
    amount = db.Column(db.Numeric(20, 9), nullable=False)  # TON amount with 9 decimals
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.tx_hash[:8]}... {self.tx_type} {self.amount}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'tx_hash': self.tx_hash,
            'type': self.tx_type,
            'amount': float(self.amount),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }


class PoolStats(db.Model):
    """Daily pool statistics snapshot"""
    __tablename__ = 'pool_stats'
    __table_args__ = {'schema': 'ton_pool'}
    
    id = db.Column(db.Integer, primary_key=True)
    
    total_staked = db.Column(db.Numeric(20, 9), default=0)
    total_participants = db.Column(db.Integer, default=0)
    apy = db.Column(db.Numeric(5, 2), default=0)  # Annual Percentage Yield
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<PoolStats {self.recorded_at} {self.total_staked} TON>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'total_staked': float(self.total_staked),
            'total_participants': self.total_participants,
            'apy': float(self.apy),
            'recorded_at': self.recorded_at.isoformat()
        }


class Subscription(db.Model):
    """User subscriptions via Stripe"""
    __tablename__ = 'subscriptions'
    __table_args__ = {'schema': 'ton_pool'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ton_pool.users.id'), nullable=False)
    
    stripe_subscription_id = db.Column(db.String(100), unique=True, nullable=False)
    stripe_customer_id = db.Column(db.String(100), nullable=False)
    stripe_price_id = db.Column(db.String(100), nullable=False)  # Stripe price ID
    
    status = db.Column(db.String(20), default='active')  # active, canceled, past_due, trialing
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Subscription {self.stripe_subscription_id} {self.status}>'
