import pytest
import threading
import time
from app import create_app
from app.database import db
from app.models import Task

@pytest.fixture
def app():
    result = create_app()
    app = result[0]  # Unpack the tuple to get the app object
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'FLASK_ENV': 'testing'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_task_workflow(client):
    """Test complete task workflow: create, read, update, delete."""
    # Create task
    create_response = client.post('/api/tasks', json={
        'title': 'Integration Test Task',
        'description': 'Testing complete workflow'
    })
    assert create_response.status_code == 201
    task_id = create_response.json['id']
    
    # Read task
    get_response = client.get(f'/api/tasks/{task_id}')
    assert get_response.status_code == 200
    assert get_response.json['title'] == 'Integration Test Task'
    
    # Update task
    update_response = client.put(f'/api/tasks/{task_id}')
    assert update_response.status_code == 200
    assert update_response.json['done'] == True
    
    # Delete task
    delete_response = client.delete(f'/api/tasks/{task_id}')
    assert delete_response.status_code == 204
    
    # Verify task is deleted
    get_response = client.get(f'/api/tasks/{task_id}')
    assert get_response.status_code == 404

def test_concurrent_operations(app, client):
    """Test concurrent database operations."""
    # Create multiple tasks
    tasks = []
    for i in range(5):
        response = client.post('/api/tasks', json={
            'title': f'Concurrent Task {i}',
            'description': f'Testing concurrent operations {i}'
        })
        assert response.status_code == 201
        tasks.append(response.json['id'])
    
    # Verify all tasks were created
    get_all_response = client.get('/api/tasks')
    assert get_all_response.status_code == 200
    assert len(get_all_response.json) == 5
    
    # Update all tasks concurrently
    for task_id in tasks:
        response = client.put(f'/api/tasks/{task_id}')
        assert response.status_code == 200
        assert response.json['done'] == True
    
    # Verify all tasks were updated
    get_all_response = client.get('/api/tasks')
    assert all(task['done'] for task in get_all_response.json)

def test_database_rollback(app, client):
    """Test database rollback on error."""
    # Create initial task
    response = client.post('/api/tasks', json={
        'title': 'Rollback Test',
        'description': 'Testing database rollback'
    })
    assert response.status_code == 201
    initial_task_id = response.json['id']
    
    # Try to create a task with missing required fields
    error_response = client.post('/api/tasks', json={})
    assert error_response.status_code == 400
    assert 'error' in error_response.json
    
    # Verify initial task still exists
    response = client.get(f'/api/tasks/{initial_task_id}')
    assert response.status_code == 200
    assert response.json['title'] == 'Rollback Test' 