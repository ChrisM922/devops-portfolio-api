import os
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Get database URI from environment
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # Parse DATABASE_URL for Render
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL

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
