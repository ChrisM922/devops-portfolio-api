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

@pytest.fixture
def sample_task(app):
    """Create a sample task for testing."""
    with app.app_context():
        task = Task(title='Sample Task', description='Sample Description')
        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)  # Ensure task is refreshed from database
        return task

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert response.json['database'] == 'connected'

def test_index_page(client):
    """Test the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Task List' in response.data

def test_create_task(client):
    """Test creating a new task."""
    # Test with JSON data
    response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'
    assert response.json['description'] == 'Test Description'
    assert not response.json['done']

    # Test with form data
    response = client.post('/api/tasks', data={
        'title': 'Form Task',
        'description': 'Form Description'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'Form Task'
    assert response.json['description'] == 'Form Description'

    # Test with missing data
    response = client.post('/api/tasks', json={})
    assert response.status_code == 500

def test_get_tasks(client, sample_task):
    """Test retrieving all tasks."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['title'] == 'Sample Task'
    assert response.json[0]['description'] == 'Sample Description'
    assert not response.json[0]['done']

def test_get_task(client, sample_task):
    """Test retrieving a specific task."""
    # Test existing task
    response = client.get(f'/api/tasks/{sample_task.id}')
    assert response.status_code == 200
    assert response.json['title'] == 'Sample Task'
    assert response.json['description'] == 'Sample Description'

    # Test non-existent task
    response = client.get('/api/tasks/999')
    assert response.status_code == 404

def test_update_task(client, sample_task):
    """Test updating a task."""
    # Test toggling task completion
    response = client.put(f'/api/tasks/{sample_task.id}')
    assert response.status_code == 200
    assert response.json['done'] == True

    # Test updating non-existent task
    response = client.put('/api/tasks/999')
    assert response.status_code == 404

def test_delete_task(client, sample_task):
    """Test deleting a task."""
    # Test deleting existing task
    response = client.delete(f'/api/tasks/{sample_task.id}')
    assert response.status_code == 200
    assert response.json['message'] == 'Task deleted'

    # Verify task is deleted
    response = client.get(f'/api/tasks/{sample_task.id}')
    assert response.status_code == 404

    # Test deleting non-existent task
    response = client.delete('/api/tasks/999')
    assert response.status_code == 404

def test_invalid_methods(client):
    """Test invalid HTTP methods."""
    # Test PUT on /api/tasks
    response = client.put('/api/tasks')
    assert response.status_code == 405

    # Test DELETE on /api/tasks
    response = client.delete('/api/tasks')
    assert response.status_code == 405

def test_error_handling(client):
    """Test error handling."""
    # Test 404 error
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert response.json['error'] == 'Resource not found'

    # Test 500 error (by causing a database error)
    response = client.post('/api/tasks', json={'invalid': 'data'})
    assert response.status_code == 500
    assert 'error' in response.json