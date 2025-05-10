from flask import request, jsonify, render_template
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    from app.database import db
    from app.models import Task

    @app.route('/health')
    def health_check():
        try:
            # Test database connection using text()
            db.session.execute(text('SELECT 1'))
            logger.info("Health check passed")
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.route('/')
    def index():
        logger.info("Accessing index page")
        tasks = Task.query.all()
        return render_template('index.html', tasks=tasks)

    @app.route('/api/tasks', methods=['POST'])
    def create_task():
        try:
            data = request.form if request.form else request.get_json()
            task = Task(
                title=data.get('title'),
                description=data.get('description')
            )
            db.session.add(task)
            db.session.commit()
            logger.info(f"Created new task: {task.title}")
            if request.headers.get('HX-Request'):
                return render_template('_task.html', task=task)
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'done': task.done
            }), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating task: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/tasks', methods=['GET'])
    def get_tasks():
        try:
            tasks = Task.query.all()
            logger.info(f"Retrieved {len(tasks)} tasks")
            if request.headers.get('HX-Request'):
                return render_template('index.html', tasks=tasks)
            return jsonify([
                {
                    'id': t.id,
                    'title': t.title,
                    'description': t.description,
                    'done': t.done
                } for t in tasks
            ])
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error retrieving tasks: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        try:
            task = db.session.get(Task, task_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
                return jsonify({'error': 'Task not found'}), 404
            logger.info(f"Retrieved task {task_id}")
            if request.headers.get('HX-Request'):
                return render_template('_task.html', task=task)
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'done': task.done
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        try:
            task = db.session.get(Task, task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for update")
                return jsonify({'error': 'Task not found'}), 404
            
            # Toggle the done status
            task.done = not task.done
            db.session.commit()
            logger.info(f"Updated task {task_id} status to {task.done}")
            
            if request.headers.get('HX-Request'):
                return render_template('_task.html', task=task)
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'done': task.done
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating task {task_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        try:
            task = db.session.get(Task, task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for deletion")
                return jsonify({'error': 'Task not found'}), 404
            db.session.delete(task)
            db.session.commit()
            logger.info(f"Deleted task {task_id}")
            if request.headers.get('HX-Request'):
                return ''
            return jsonify({'message': 'Task deleted'})
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
