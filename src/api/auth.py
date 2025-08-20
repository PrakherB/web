"""
Authentication and authorization module
"""
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
import hashlib
import secrets

class AuthManager:
    def __init__(self):
        self.secret_key = secrets.token_hex(32)
        self.api_keys = {}  # In production, use a database
    
    def generate_token(self, user_id, expires_in=3600):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def generate_api_key(self, user_id, description=""):
        """Generate API key"""
        api_key = secrets.token_hex(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[key_hash] = {
            'user_id': user_id,
            'description': description,
            'created_at': datetime.utcnow().isoformat(),
            'last_used': None,
            'usage_count': 0
        }
        
        return api_key
    
    def validate_api_key(self, api_key):
        """Validate API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.api_keys:
            self.api_keys[key_hash]['last_used'] = datetime.utcnow().isoformat()
            self.api_keys[key_hash]['usage_count'] += 1
            return True
        return False

auth_manager = AuthManager()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        api_key = request.headers.get('X-API-Key')
        
        if api_key:
            if not auth_manager.validate_api_key(api_key):
                return jsonify({'error': 'Invalid API key'}), 401
        elif token:
            if not token.startswith('Bearer '):
                return jsonify({'error': 'Invalid token format'}), 401
            
            token = token.split(' ')[1]
            payload = auth_manager.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
        else:
            return jsonify({'error': 'Authentication required'}), 401
            
        return f(*args, **kwargs)
    return decorated_function
