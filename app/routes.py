from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import text
from app.models import Task
from app.database import db
from prometheus_client import Counter
import logging

# Set up logging
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

# Create blueprint
bp = Blueprint('tasks', __name__)

# Prometheus metrics
task_operations = Counter('task_operations_total', 'Total task operations', ['operation'])

@bp.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        logger.info("Health check passed")
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "error", "error": f"Database connection error: {str(e)}"}), 500

@bp.route('/')
def index():
    """Render the main page."""
    try:
        tasks = Task.query.all()
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return render_template('index.html', tasks=[]), 500

@bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    try:
        tasks = Task.query.all()
        task_operations.labels(operation='list').inc()
        logger.info("Retrieved all tasks")
        return jsonify([task.to_dict() for task in tasks]), 200
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    try:
        if request.headers.get('HX-Request'):
            data = request.form
        elif request.is_json:
            data = request.get_json()
        else:
            data = request.form

        title = data.get('title')
        description = data.get('description', '')

        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()

        task_operations.labels(operation='create').inc()
        logger.info(f"Created new task: {title}")
        
        if request.headers.get('HX-Request'):
            return render_template('partials/task.html', task=task), 201
        return jsonify(task.to_dict()), 201
    except ValueError as e:
        logger.error(f"Validation error creating task: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    try:
        task = Task.query.get(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            return jsonify({"error": "Task not found"}), 404

        task_operations.labels(operation='get').inc()
        logger.info(f"Retrieved task {task_id}")
        return jsonify(task.to_dict()), 200
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task's completion status."""
    try:
        task = Task.query.get(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            return jsonify({"error": "Task not found"}), 404

        task.completed = not task.completed
        db.session.commit()

        task_operations.labels(operation='update').inc()
        logger.info(f"Updated task {task_id} completion status to {task.completed}")

        # Check if it's an HTMX request
        if request.headers.get('HX-Request'):
            return render_template('partials/task.html', task=task), 200
        
        return jsonify(task.to_dict()), 200
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    try:
        task = Task.query.get(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            return jsonify({"error": "Task not found"}), 404

        db.session.delete(task)
        db.session.commit()
        
        task_operations.labels(operation='delete').inc()
        logger.info(f"Deleted task {task_id}")
        if request.headers.get('HX-Request'):
            return '', 200
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
