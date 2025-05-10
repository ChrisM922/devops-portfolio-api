import os
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Get database URI from environment
    DATABASE_URL = SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    
    # Parse DATABASE_URL for Render
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    def __init__(self):
        # Update database URI from environment if available
        if 'DATABASE_URL' in os.environ:
            self.DATABASE_URL = os.environ['DATABASE_URL']
            if self.DATABASE_URL.startswith('postgres://'):
                self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            else:
                self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
