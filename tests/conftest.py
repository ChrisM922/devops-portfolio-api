import os
import pytest

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables before each test."""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['FLASK_APP'] = 'app.main:app'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
    yield
    # Cleanup after tests
    for key in ['FLASK_ENV', 'FLASK_APP', 'SQLALCHEMY_DATABASE_URI', 'SQLALCHEMY_TRACK_MODIFICATIONS']:
        os.environ.pop(key, None) 