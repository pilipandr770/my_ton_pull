"""
Authentication utilities and decorators
"""

from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User


def login_required(fn):
    """Decorator to require authentication via JWT"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    return wrapper


def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_admin():
                return jsonify({'error': 'Admin access required'}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'message': str(e)}), 401
    return wrapper


def subscription_required(fn):
    """Decorator to require active subscription"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.has_active_subscription() and not user.is_admin():
                return jsonify({
                    'error': 'Active subscription required',
                    'subscription_status': user.subscription_status,
                    'subscription_expires_at': user.subscription_expires_at.isoformat() if user.subscription_expires_at else None
                }), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'message': str(e)}), 401
    return wrapper


def get_current_user():
    """Get current authenticated user from JWT"""
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return User.query.get(user_id)
    except:
        pass
    return None
