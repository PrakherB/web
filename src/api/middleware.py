"""
API middleware for request processing
"""
from flask import request, jsonify
import time
import logging
from functools import wraps

def setup_middleware(app):
    """Setup middleware for the Flask app"""
    
    @app.before_request
    def before_request():
        request.start_time = time.time()
        logging.info(f"Request: {request.method} {request.url}")
    
    @app.after_request
    def after_request(response):
        duration = time.time() - request.start_time
        logging.info(f"Response: {response.status_code} in {duration:.3f}s")
        response.headers['X-Response-Time'] = str(duration)
        return response

def rate_limit(max_requests=100, window=3600):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting (use Redis in production)
            client_ip = request.remote_addr
            # Implementation would go here
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_api_key(f):
    """API key authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key (implement your logic)
        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(api_key):
    """Validate API key - implement your logic"""
    # Placeholder implementation
    return True
