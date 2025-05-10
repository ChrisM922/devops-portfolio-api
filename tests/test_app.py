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

def test_create_task_htmx(client):
    """Test creating a task with HTMX request."""
    response = client.post('/api/tasks', 
        data={'title': 'HTMX Task', 'description': 'HTMX Description'},
        headers={'HX-Request': 'true'}
    )
    assert response.status_code == 201
    assert b'HTMX Task' in response.data
    assert b'HTMX Description' in response.data
    assert b'Complete' in response.data  # Button text for incomplete task

def test_get_tasks_htmx(client, sample_task):
    """Test retrieving tasks with HTMX request."""
    response = client.get('/api/tasks', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert b'Sample Task' in response.data
    assert b'Sample Description' in response.data

def test_get_task_htmx(client, sample_task):
    """Test retrieving a specific task with HTMX request."""
    response = client.get(f'/api/tasks/{sample_task.id}', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert b'Sample Task' in response.data
    assert b'Sample Description' in response.data

def test_update_task_htmx(client, sample_task):
    """Test updating a task with HTMX request."""
    response = client.put(f'/api/tasks/{sample_task.id}', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert b'line-through' in response.data  # Task is marked as done
    assert b'Undo' in response.data  # Button text for completed task

def test_delete_task_htmx(client, sample_task):
    """Test deleting a task with HTMX request."""
    response = client.delete(f'/api/tasks/{sample_task.id}', headers={'HX-Request': 'true'})
    assert response.status_code == 200
    assert response.data == b''  # Empty response for HTMX delete

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
    assert response.status_code == 500
    assert 'error' in response.json

    # Test with invalid title type
    response = client.post('/api/tasks', json={'title': 123, 'description': 'Invalid title type'})
    assert response.status_code == 500
    assert 'error' in response.json

    # Test with invalid description type
    response = client.post('/api/tasks', json={'title': 'Valid title', 'description': ['Invalid description type']})
    assert response.status_code == 500
    assert 'error' in response.json

def test_database_connection_error(app, client):
    """Test handling of database connection errors."""
    # Temporarily modify database URI to an invalid one
    original_uri = app.config['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nonexistent/path/db.sqlite'
    
    try:
        response = client.get('/health')
        assert response.status_code == 500
        assert response.json['status'] == 'unhealthy'
        assert 'error' in response.json
    finally:
        # Restore original database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = original_uri

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
    assert response.status_code == 500
    
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

def test_app_configuration():
    """Test application configuration loading."""
    from app.config import Config
    
    # Test default configuration
    assert Config.SQLALCHEMY_TRACK_MODIFICATIONS == False
    assert 'SQLALCHEMY_DATABASE_URI' in Config.__dict__
    assert 'SQLALCHEMY_ENGINE_OPTIONS' in Config.__dict__
    assert Config.SQLALCHEMY_ENGINE_OPTIONS['pool_pre_ping'] == True
    assert Config.SQLALCHEMY_ENGINE_OPTIONS['pool_recycle'] == 300

def test_app_initialization():
    """Test application initialization."""
    from app import create_app
    from app.config import Config
    
    # Test with default configuration
    app = create_app()
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
    assert 'SQLALCHEMY_DATABASE_URI' in app.config
    
    # Test with custom configuration
    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    app = create_app(TestConfig)
    assert app.config['TESTING'] == True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'

def test_environment_variables():
    """Test environment variable handling."""
    import os
    from app.config import Config
    
    # Test DATABASE_URL parsing
    os.environ['DATABASE_URL'] = 'postgres://user:pass@host:5432/db'
    config = Config()
    assert config.SQLALCHEMY_DATABASE_URI == 'postgresql://user:pass@host:5432/db'
    
    # Test default SQLite database
    os.environ.pop('DATABASE_URL', None)
    config = Config()
    assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///app.db'

def test_prometheus_metrics(client):
    """Test Prometheus metrics collection."""
    # Create a task to trigger metrics
    response = client.post('/api/tasks', json={
        'title': 'Metrics Test',
        'description': 'Testing Prometheus metrics'
    })
    assert response.status_code == 201
    
    # Get metrics endpoint
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'task_operations_total' in response.data
    assert b'operation="create"' in response.data

def test_logging_configuration(app):
    """Test logging configuration."""
    import logging
    
    # Check if logger is configured
    logger = logging.getLogger(__name__)
    assert logger.level == logging.INFO
    
    # Check if handlers are configured
    assert len(logger.handlers) > 0
    
    # Test logging format
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, logging.Formatter)
    assert '%(asctime)s' in handler.formatter._fmt
    assert '%(name)s' in handler.formatter._fmt
    assert '%(levelname)s' in handler.formatter._fmt
    assert '%(message)s' in handler.formatter._fmt

def test_application_logging(client, caplog):
    """Test application logging during operations."""
    with caplog.at_level(logging.INFO):
        # Test task creation logging
        response = client.post('/api/tasks', json={
            'title': 'Logging Test',
            'description': 'Testing application logging'
        })
        assert response.status_code == 201
        assert 'Created new task: Logging Test' in caplog.text
        
        # Test task retrieval logging
        response = client.get('/api/tasks')
        assert response.status_code == 200
        assert 'Retrieved' in caplog.text and 'tasks' in caplog.text
        
        # Test error logging
        response = client.post('/api/tasks', json={'invalid': 'data'})
        assert response.status_code == 500
        assert 'Error creating task' in caplog.text