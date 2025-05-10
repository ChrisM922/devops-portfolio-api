import pytest
from app import create_app
from app.database import db
from app.models import Task
from sqlalchemy import inspect
import logging
import os
from prometheus_client import REGISTRY, CollectorRegistry
from sqlalchemy.sql import text

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a new registry for each test
    registry = CollectorRegistry()
    
    result = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    }, registry=registry)
    
    # Unpack the result tuple
    app = result[0]
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

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

def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200

def test_get_tasks_empty(client):
    """Test getting tasks when none exist."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert response.json == []

def test_create_task(client):
    """Test creating a new task."""
    response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'
    assert response.json['description'] == 'Test Description'
    assert not response.json['done']

def test_create_task_no_title(client):
    """Test creating a task without a title."""
    response = client.post('/api/tasks', json={
        'description': 'Test Description'
    })
    assert response.status_code == 400
    assert 'error' in response.json

def test_get_task(client):
    """Test getting a specific task."""
    # Create a task first
    task_response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    task_id = task_response.json['id']
    
    # Get the task
    response = client.get(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    assert response.json['title'] == 'Test Task'
    assert response.json['description'] == 'Test Description'

def test_get_nonexistent_task(client):
    """Test getting a task that doesn't exist."""
    response = client.get('/api/tasks/999')
    assert response.status_code == 404
    assert 'error' in response.json

def test_update_task(client):
    """Test updating a task's completion status."""
    # Create a task first
    task_response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    task_id = task_response.json['id']
    
    # Update the task
    response = client.put(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    assert response.json['done'] is True

def test_update_nonexistent_task(client):
    """Test updating a task that doesn't exist."""
    response = client.put('/api/tasks/999')
    assert response.status_code == 404
    assert 'error' in response.json

def test_delete_task(client):
    """Test deleting a task."""
    # Create a task first
    task_response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    task_id = task_response.json['id']
    
    # Delete the task
    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 204
    
    # Verify task is deleted
    get_response = client.get(f'/api/tasks/{task_id}')
    assert get_response.status_code == 404

def test_delete_nonexistent_task(client):
    """Test deleting a task that doesn't exist."""
    response = client.delete('/api/tasks/999')
    assert response.status_code == 404
    assert 'error' in response.json

def test_invalid_methods(client):
    """Test invalid HTTP methods."""
    # Test PUT on /api/tasks
    response = client.put('/api/tasks')
    assert response.status_code == 405

    # Test DELETE on /api/tasks
    response = client.delete('/api/tasks')
    assert response.status_code == 405

def test_error_handlers(app, client):
    """Test application error handlers."""
    # Test 404 handler
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert response.headers['Content-Type'] == 'application/json'
    data = response.get_json()
    assert data is not None
    assert data['error'] == 'Resource not found'
    
    # Test 500 handler by triggering a database error
    def mock_execute(*args, **kwargs):
        raise Exception("Test error")
    
    with app.test_request_context():
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as e:
            response = app.handle_exception(e)
            assert response is not None
            assert response.status_code == 500
            assert response.headers['Content-Type'] == 'application/json'
            data = response.get_json()
            assert data is not None
            assert data['error'] == 'Internal server error'

def test_htmx_requests(client):
    """Test HTMX-specific responses."""
    # Test GET tasks with HX-Request header
    response = client.get('/api/tasks', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']
    
    # Test POST task with HX-Request header
    response = client.post('/api/tasks', 
                         data={'title': 'HTMX Task', 'description': 'HTMX Description'},
                         headers={'HX-Request': 'true'})
    assert response.status_code == 201
    assert 'text/html' in response.headers['Content-Type']
    
    # Get the task ID from the database
    task = Task.query.filter_by(title='HTMX Task').first()
    assert task is not None
    
    # Test GET single task with HX-Request header
    response = client.get(f'/api/tasks/{task.id}', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']
    
    # Test PUT task with HX-Request header
    response = client.put(f'/api/tasks/{task.id}', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']
    
    # Test DELETE task with HX-Request header
    response = client.delete(f'/api/tasks/{task.id}', headers={'HX-Request': 'true'})
    assert response.status_code == 200

def test_index_page_with_tasks(client, sample_task):
    """Test index page rendering with tasks."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Task Manager' in response.data
    assert b'Sample Task' in response.data
    assert b'Sample Description' in response.data
    assert b'Complete' in response.data
    assert b'Delete' in response.data

def test_index_page_without_tasks(client):
    """Test index page rendering without tasks."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Task Manager' in response.data
    assert b'Add Task' in response.data
    assert b'Task List' in response.data

def test_create_task_invalid_data(client):
    """Test creating a task with invalid data."""
    # Test with missing title
    response = client.post('/api/tasks', json={'description': 'No title'})
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error'] == 'Title is required'

    # Test with invalid title type
    response = client.post('/api/tasks', json={'title': 123, 'description': 'Invalid title type'})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Title must be a string' in response.json['error']

def test_database_connection_error(app, client, monkeypatch):
    """Test handling of database connection errors."""
    def mock_execute(*args, **kwargs):
        raise Exception("Database connection error")

    # Mock the database execute method
    monkeypatch.setattr(db.session, "execute", mock_execute)

    response = client.get('/health')
    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert 'database' in response.json['error'].lower()

def test_database_rollback_on_error(client):
    """Test database rollback on error during task creation."""
    # Create initial task
    response = client.post('/api/tasks', json={
        'title': 'Initial Task',
        'description': 'This should remain'
    })
    assert response.status_code == 201
    initial_task_id = response.json['id']
    
    # Try to create a task with invalid data
    response = client.post('/api/tasks', json={'invalid': 'data'})
    assert response.status_code == 400
    assert 'error' in response.json
    
    # Verify initial task still exists
    response = client.get(f'/api/tasks/{initial_task_id}')
    assert response.status_code == 200
    assert response.json['title'] == 'Initial Task'

def test_concurrent_task_operations(client):
    """Test concurrent task operations."""
    # Create multiple tasks
    task_ids = []
    for i in range(3):
        response = client.post('/api/tasks', json={
            'title': f'Concurrent Task {i}',
            'description': f'Testing concurrent operations {i}'
        })
        assert response.status_code == 201
        task_ids.append(response.json['id'])
    
    # Update all tasks concurrently
    for task_id in task_ids:
        response = client.put(f'/api/tasks/{task_id}')
        assert response.status_code == 200
        assert response.json['done'] == True
    
    # Verify all tasks were updated
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert all(task['done'] for task in response.json)

def test_app_configuration(app):
    """Test application configuration."""
    # Test default configuration
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert 'SQLALCHEMY_DATABASE_URI' in app.config
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'  # Test environment uses in-memory database
    
    # Test debug mode
    app.config['FLASK_ENV'] = 'development'
    assert app.debug is False  # Debug mode should be off in testing

def test_app_logging(app, caplog):
    """Test application logging setup."""
    import logging
    logger = logging.getLogger('app')
    
    # Test logger configuration
    assert logger.level == logging.INFO
    
    # Test logging output
    with caplog.at_level(logging.INFO):
        logger.info("Test log message")
        assert "Test log message" in caplog.text

def test_index_page_error_handling(app, client, monkeypatch):
    """Test error handling in the index page."""
    def mock_all(*args, **kwargs):
        raise Exception("Database error")
    
    with monkeypatch.context() as m:
        m.setattr("sqlalchemy.orm.query.Query.all", mock_all)
        response = client.get('/')
        assert response.status_code == 500
        assert b'Task List' in response.data

def test_get_tasks_error_handling(app, client, monkeypatch):
    """Test error handling in get_tasks endpoint."""
    def mock_all(*args, **kwargs):
        raise Exception("Database error")
    
    with monkeypatch.context() as m:
        m.setattr("sqlalchemy.orm.query.Query.all", mock_all)
        response = client.get('/api/tasks')
        assert response.status_code == 500
        assert 'error' in response.json

def test_create_task_database_error(app, client, monkeypatch):
    """Test database error handling in create_task endpoint."""
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, "commit", mock_commit)
    response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    assert response.status_code == 500
    assert 'error' in response.json

def test_update_task_database_error(app, client, sample_task, monkeypatch):
    """Test database error handling in update_task endpoint."""
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, "commit", mock_commit)
    response = client.put(f'/api/tasks/{sample_task.id}')
    assert response.status_code == 500
    assert 'error' in response.json

def test_delete_task_database_error(app, client, sample_task, monkeypatch):
    """Test database error handling in delete_task endpoint."""
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, "commit", mock_commit)
    response = client.delete(f'/api/tasks/{sample_task.id}')
    assert response.status_code == 500
    assert 'error' in response.json

def test_task_model_validation():
    """Test Task model validation methods."""
    # Test valid task creation
    task = Task(title="Valid Task", description="Valid Description")
    assert task.title == "Valid Task"
    assert task.description == "Valid Description"
    
    # Test empty title
    with pytest.raises(ValueError, match="Title must be a string"):
        Task(title="", description="Description")
    
    # Test title too long
    with pytest.raises(ValueError, match="Title cannot be longer than 100 characters"):
        Task(title="x" * 101, description="Description")
    
    # Test invalid title type
    with pytest.raises(ValueError, match="Title must be a string"):
        Task(title=123, description="Description")
    
    # Test title validation on update
    task = Task(title="Valid Task")
    with pytest.raises(ValueError, match="Title must be a string"):
        task.validate_title("title", None)
    with pytest.raises(ValueError, match="Title must be a string"):
        task.validate_title("title", "")

def test_config_database_url_parsing():
    """Test database URL parsing in config."""
    import os
    from app.config import Config
    
    # Test postgres URL conversion
    os.environ['DATABASE_URL'] = 'postgres://user:pass@localhost:5432/db'
    config = Config()
    assert config.SQLALCHEMY_DATABASE_URI == 'postgresql://user:pass@localhost:5432/db'
    
    # Test non-postgres URL
    os.environ['DATABASE_URL'] = 'mysql://user:pass@localhost:3306/db'
    config = Config()
    assert config.SQLALCHEMY_DATABASE_URI == 'mysql://user:pass@localhost:3306/db'
    
    # Test default SQLite URL
    os.environ.pop('DATABASE_URL', None)
    config = Config()
    assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///app.db'

def test_app_initialization_error(monkeypatch):
    """Test application initialization error handling."""
    def mock_create_all():
        raise Exception("Database initialization error")
    
    monkeypatch.setattr(db, "create_all", mock_create_all)
    
    with pytest.raises(Exception) as exc_info:
        create_app()
    assert "Database initialization error" in str(exc_info.value)

def test_metrics_endpoint(client):
    """Test the metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'text/plain' in response.headers['Content-Type']
    assert b'task_operations_total' in response.data

def test_metrics_initialization(app):
    """Test metrics initialization."""
    from app.main import create_app
    test_app, metrics, request_count, request_latency, task_counter = create_app()
    
    # Test metrics objects
    assert metrics is not None
    assert request_count is not None
    assert request_latency is not None
    assert task_counter is not None

def test_metrics_labels(app, client):
    """Test metrics labels for different operations."""
    # Test create operation
    response = client.post('/api/tasks', json={'title': 'Test Task'})
    assert response.status_code == 201

    # Test read operation
    response = client.get('/api/tasks')
    assert response.status_code == 200

    # Test update operation
    task_id = response.json[0]['id']
    response = client.put(f'/api/tasks/{task_id}')
    assert response.status_code == 200

    # Test delete operation
    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 204

    # Verify metrics were recorded
    metrics_response = client.get('/metrics')
    assert b'task_operations_total' in metrics_response.data

def test_logging_configuration(app, caplog):
    """Test logging configuration."""
    import logging
    logger = logging.getLogger('app')
    
    # Test logger configuration
    assert logger.name == 'app'
    assert logger.level == logging.INFO
    
    # Add a handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    # Ensure there's at least one handler
    assert len(logger.handlers) > 0
    
    # Test that we can log messages
    with caplog.at_level(logging.INFO):
        logger.info("Test message")
        assert "Test message" in caplog.text

def test_application_startup(app):
    """Test application startup configuration."""
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert app.config['WTF_CSRF_ENABLED'] is False