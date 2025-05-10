import pytest
from app import create_app
from app.models import Task
from app.database import db
from sqlalchemy import inspect
import logging

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/test_db'
    app.config['FLASK_ENV'] = 'test'
    
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

def test_create_task(client):
    response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'

def test_get_tasks(client):
    # Create a task first
    client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert len(response.json) > 0 