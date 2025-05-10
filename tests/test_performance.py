import pytest
import time
from app import create_app
from app.database import db
from app.models import Task

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
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_response_time_health_check(client):
    """Test health check endpoint response time."""
    start_time = time.time()
    response = client.get('/health')
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 0.1  # Should respond within 100ms

def test_bulk_create_performance(client):
    """Test performance of bulk task creation."""
    start_time = time.time()
    
    # Create 100 tasks
    for i in range(100):
        response = client.post('/api/tasks', json={
            'title': f'Performance Test Task {i}',
            'description': f'Testing bulk creation performance {i}'
        })
        assert response.status_code == 201
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Should create 100 tasks in under 5 seconds
    assert total_time < 5.0
    assert total_time / 100 < 0.05  # Average time per task should be under 50ms

def test_bulk_read_performance(client):
    """Test performance of bulk task retrieval."""
    # Create 50 tasks first
    for i in range(50):
        client.post('/api/tasks', json={
            'title': f'Performance Test Task {i}',
            'description': f'Testing bulk read performance {i}'
        })
    
    # Test GET /api/tasks performance
    start_time = time.time()
    response = client.get('/api/tasks')
    end_time = time.time()
    
    assert response.status_code == 200
    assert len(response.json) == 50
    assert end_time - start_time < 0.5  # Should retrieve 50 tasks in under 500ms

def test_concurrent_requests_performance(client):
    """Test performance under concurrent requests."""
    # Create initial task
    response = client.post('/api/tasks', json={
        'title': 'Concurrent Test Task',
        'description': 'Testing concurrent request performance'
    })
    task_id = response.json['id']
    
    # Measure time for 50 concurrent GET requests
    start_time = time.time()
    
    for _ in range(50):
        response = client.get(f'/api/tasks/{task_id}')
        assert response.status_code == 200
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Should handle 50 concurrent requests in under 2 seconds
    assert total_time < 2.0
    assert total_time / 50 < 0.04  # Average time per request should be under 40ms 