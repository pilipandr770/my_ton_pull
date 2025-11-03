# backend/auth.py
"""
Authentication utilities and decorators
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            from flask_jwt_extended import get_jwt
            claims = get_jwt() or {}
            if claims.get('role') != 'admin':
                return jsonify({'error': 'Admin required'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Admin required', 'message': str(e)}), 403
    return wrapper

def subscription_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            from flask_jwt_extended import get_jwt
            claims = get_jwt() or {}
            if claims.get('subscription_status') != 'active':
                return jsonify({'error': 'Active subscription required'}), 402
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Subscription required', 'message': str(e)}), 402
    return wrapper
