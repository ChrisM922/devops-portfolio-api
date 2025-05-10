from flask import Blueprint, jsonify, request, render_template, current_app
from sqlalchemy import text
from app.models import Task
from app.database import db
import logging

# Set up logging
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the index page."""
    try:
        tasks = Task.query.all()
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        return render_template('index.html', error=str(e)), 500

@bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    try:
        tasks = Task.query.all()
        if request.headers.get('HX-Request'):
            return render_template('task_list.html', tasks=tasks)
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    try:
        data = request.get_json() if request.is_json else request.form
        if not data or 'title' not in data:
            return jsonify({"error": "Title is required"}), 400
        
        if not isinstance(data['title'], str):
            return jsonify({"error": "Title must be a string"}), 400
        
        task = Task(title=data['title'], description=data.get('description', ''))
        db.session.add(task)
        db.session.commit()
        
        logger.info(f"Created new task: {task.title}")
        
        if request.headers.get('HX-Request'):
            return render_template('task.html', task=task), 201
        return jsonify(task.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    try:
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        if request.headers.get('HX-Request'):
            return render_template('task.html', task=task)
        return jsonify(task.to_dict())
    
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task's completion status."""
    try:
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        task.done = not task.done
        db.session.commit()
        
        logger.info(f"Updated task {task_id} completion status to {task.done}")
        
        if request.headers.get('HX-Request'):
            return render_template('task.html', task=task)
        return jsonify(task.to_dict())
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    try:
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        logger.info(f"Deleted task {task_id}")
        
        if request.headers.get('HX-Request'):
            return '', 200
        return '', 204
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
