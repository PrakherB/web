"""
Database configuration
"""
import os
from urllib.parse import quote_plus

class DatabaseConfig:
    """Database configuration"""
    
    # SQLite configuration (default for development)
    SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'naics_classification.db')
    
    # PostgreSQL configuration
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'naics_user')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'naics_password')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'naics_classification')
    
    # MySQL configuration
    MYSQL_USER = os.environ.get('MYSQL_USER', 'naics_user')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'naics_password')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'naics_classification')
    
    @classmethod
    def get_database_uri(cls, db_type='sqlite'):
        """Get database URI based on type"""
        if db_type.lower() == 'postgresql':
            password = quote_plus(cls.POSTGRES_PASSWORD)
            return f"postgresql://{cls.POSTGRES_USER}:{password}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        
        elif db_type.lower() == 'mysql':
            password = quote_plus(cls.MYSQL_PASSWORD)
            return f"mysql+pymysql://{cls.MYSQL_USER}:{password}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DB}"
        
        else:  # Default to SQLite
            return f"sqlite:///{cls.SQLITE_DB_PATH}"
    
    @classmethod
    def get_redis_uri(cls):
        """Get Redis URI for caching"""
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = os.environ.get('REDIS_PORT', '6379')
        redis_db = os.environ.get('REDIS_DB', '0')
        redis_password = os.environ.get('REDIS_PASSWORD', '')
        
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        else:
            return f"redis://{redis_host}:{redis_port}/{redis_db}"
