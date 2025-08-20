"""
Enhanced configuration settings for NAICS Classification System - Phase 2
"""
import os
from pathlib import Path
from .database import DatabaseConfig

class Settings:
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Database settings
    DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')
    SQLALCHEMY_DATABASE_URI = DatabaseConfig.get_database_uri(DATABASE_TYPE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis settings
    REDIS_URL = DatabaseConfig.get_redis_uri()
    CACHE_TYPE = "redis" if os.environ.get('REDIS_HOST') else "simple"
    
    # API settings
    API_HOST = os.environ.get('API_HOST', '0.0.0.0')
    API_PORT = int(os.environ.get('API_PORT', 5000))
    API_DEBUG = os.environ.get('API_DEBUG', 'False').lower() == 'true'
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    
    # Classification settings
    CLASSIFICATION_CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 0.7))
    MAX_BATCH_SIZE = int(os.environ.get('MAX_BATCH_SIZE', 100))
    
    # Content extraction settings
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1000000))  # 1MB
    USER_AGENT = os.environ.get('USER_AGENT', 'NAICS-Classifier-Bot/2.0')
    
    # ML Model settings
    MODEL_PATH = DATA_DIR / "models"
    MODEL_PATH.mkdir(exist_ok=True)
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = LOGS_DIR / "naics_classifier.log"
    
    # Feature flags
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'True').lower() == 'true'
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'True').lower() == 'true'
    ENABLE_BATCH_PROCESSING = os.environ.get('ENABLE_BATCH_PROCESSING', 'True').lower() == 'true'
    
    # External service settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    
    # Monitoring settings
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    PROMETHEUS_PORT = int(os.environ.get('PROMETHEUS_PORT', 8000))
    
    @classmethod
    def load_env_file(cls, env_file=".env"):
        """Load environment variables from file"""
        env_path = cls.BASE_DIR / env_file
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ.setdefault(key, value)

# Load environment variables
Settings.load_env_file()
