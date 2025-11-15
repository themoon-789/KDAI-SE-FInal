"""
Authentication and Authorization
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request
from models import User, db
from datetime import datetime

jwt = JWTManager()

def init_auth(app):
    """Initialize authentication"""
    jwt.init_app(app)

def login_required(fn):
    """Decorator to require authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    return wrapper

def role_required(*roles):
    """Decorator to require specific role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                
                if not user or user.role not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
        return wrapper
    return decorator

def authenticate_user(username, password):
    """Authenticate user and return tokens"""
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return None, None
    
    if not user.is_active:
        return None, None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return access_token, refresh_token

def get_current_user():
    """Get current authenticated user"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None
