import pytest
from app import create_app
from app.database import db
from app.models import Task
from sqlalchemy import inspect
import logging
import os

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'FLASK_ENV': 'testing'
    })
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            
            # Verify table exists
            inspector = inspect(db.engine)
            if 'task' not in inspector.get_table_names():
                raise Exception("Test database initialization failed")
                
            yield app
            
        except Exception as e:
            app.logger.error(f"Test setup failed: {str(e)}")
            raise
        finally:
            # Cleanup
            db.session.remove()
            db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert response.json['database'] == 'connected'

def test_create_task(client):
    response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'
    assert response.json['description'] == 'Test Description'
    assert not response.json['done']

def test_get_tasks(client):
    # Create a test task first
    client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['title'] == 'Test Task'
    assert response.json[0]['description'] == 'Test Description'
    assert not response.json[0]['done'] 