"""
Database models for TON Staking Pool
Uses separate schema 'ton_pool' for multi-project PostgreSQL database
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User accounts in the staking pool"""
    __tablename__ = 'users'
    __table_args__ = {'schema': 'ton_pool'}
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', back_populates='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.wallet_address[:8]}...>'


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
    
    status = db.Column(db.String(20), default='active')  # active, canceled, past_due
    current_period_end = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subscription {self.stripe_subscription_id} {self.status}>'
