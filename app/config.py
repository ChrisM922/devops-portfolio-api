import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')


class Config:
    # Use the Render database URL
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
