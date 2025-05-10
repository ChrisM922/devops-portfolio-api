# Test Suite Documentation

This directory contains the test suite for the Task Management API. The tests are organized into three main categories:

## 1. Unit Tests (`test_app.py`)

Basic unit tests for individual components and endpoints:

- Health check endpoint
- Task creation (JSON and form data)
- Task retrieval (single and all tasks)
- Task updates
- Task deletion
- Error handling
- Invalid methods

## 2. Integration Tests (`test_integration.py`)

Tests that verify the interaction between different components:

- Complete task workflow (CRUD operations)
- Concurrent database operations
- Database rollback on errors
- Transaction handling

## 3. Performance Tests (`test_performance.py`)

Tests that measure the application's performance:

- Response time for health check
- Bulk task creation performance
- Bulk task retrieval performance
- Concurrent request handling

## Running Tests

### Basic Test Run

```bash
pytest
```

### With Coverage Report

```bash
pytest --cov=app tests/ --cov-report=term-missing
```

### Specific Test Categories

```bash
# Run only unit tests
pytest tests/test_app.py

# Run only integration tests
pytest tests/test_integration.py

# Run only performance tests
pytest tests/test_performance.py
```

### Performance Benchmarking

```bash
pytest tests/test_performance.py --benchmark-only
```

## Test Configuration

Tests use an in-memory SQLite database by default. The configuration is set in the test fixtures:

```python
app.config.update({
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'FLASK_ENV': 'testing'
})
```

## Performance Thresholds

The performance tests enforce the following thresholds:

- Health check response: < 100ms
- Bulk task creation (100 tasks): < 5 seconds
- Bulk task retrieval (50 tasks): < 500ms
- Concurrent requests (50 requests): < 2 seconds

## Adding New Tests

When adding new tests:

1. Choose the appropriate test file based on the test type
2. Follow the existing patterns for fixtures and assertions
3. Add docstrings explaining the test purpose
4. Update this documentation if adding new test categories

## Continuous Integration

Tests are automatically run in the GitHub Actions workflow:

1. Unit and integration tests run on every push and pull request
2. Performance tests run on every push to main
3. Coverage reports are generated and uploaded to Codecov
4. Test results are reported in the GitHub Actions summary
