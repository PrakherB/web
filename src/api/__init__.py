"""
API module for NAICS Classification Service
"""
from .routes import app
from .middleware import setup_middleware
from .auth import auth_manager

__all__ = ['app', 'setup_middleware', 'auth_manager']
