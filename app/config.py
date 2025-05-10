import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database connection options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    def __init__(self):
        # Update database URI from environment if available
        if 'DATABASE_URL' in os.environ:
            self.DATABASE_URL = os.environ['DATABASE_URL']
            if self.DATABASE_URL.startswith('postgres://'):
                self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            else:
                self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
