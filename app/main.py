import os
import sys
import logging
from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import CollectorRegistry, Counter
from app.config import Config
from app.database import db
from sqlalchemy import text

def init_metrics(app, registry=None):
    """Initialize Prometheus metrics."""
    # Create a new registry if none is provided
    if registry is None:
        registry = CollectorRegistry()
    
    # Initialize metrics exporter
    metrics = PrometheusMetrics(app, registry=registry)
    metrics.info('app_info', 'Application info', version='1.0.0')
    
    # Create task operations counter directly
    task_counter = Counter(
        'task_operations_total',
        'Total number of task operations',
        ['operation'],
        registry=registry
    )
    
    # Attach the counter to the app
    app.task_counter = task_counter
    
    return metrics, task_counter

def create_app(config_class=Config, registry=None):
    app = Flask(__name__)
    
    # Handle both dict and class config
    if isinstance(config_class, dict):
        app.config.update(config_class)
    else:
        app.config.from_object(config_class)

    # Configure logging
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    
    # Create console handler if none exists
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Initialize extensions
    db.init_app(app)
    
    # Initialize metrics
    metrics, task_counter = init_metrics(app, registry)

    # Register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Create all database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Check and update database schema if needed
            try:
                # Check if the task table has timestamp columns
                result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'task' AND column_name = 'created_at'"))
                has_created_at = result.scalar() is not None
                
                result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'task' AND column_name = 'updated_at'"))
                has_updated_at = result.scalar() is not None
                
                # Add missing columns if needed
                if not has_created_at:
                    logger.info("Adding created_at column to task table")
                    db.session.execute(text("ALTER TABLE task ADD COLUMN created_at TIMESTAMP"))
                    
                if not has_updated_at:
                    logger.info("Adding updated_at column to task table")
                    db.session.execute(text("ALTER TABLE task ADD COLUMN updated_at TIMESTAMP"))
                    
                if not has_created_at or not has_updated_at:
                    db.session.commit()
                    logger.info("Database schema updated successfully")
            
            except Exception as e:
                db.session.rollback()
                logger.warning(f"Could not update database schema: {str(e)}")
                # Continue execution even if we can't add the columns
        
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {error}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    # Register the error handler explicitly
    app.register_error_handler(500, internal_error)

    # For backward compatibility with tests that expect 5 return values
    request_count = metrics.counter(
        'flask_http_request_count_dummy',
        'Dummy counter for test compatibility',
        labels={}
    )
    
    # Dummy histogram for request latency
    request_latency = metrics.histogram(
        'flask_http_request_latency_dummy',
        'Dummy histogram for test compatibility',
        labels={}
    )

    # Add metrics endpoint
    @app.route('/metrics')
    def metrics_endpoint():
        return metrics.generate_latest(), 200, {'Content-Type': 'text/plain'}

    return app, metrics, request_count, request_latency, task_counter

# Only create the global app instance if not being imported for testing
if not any(arg in sys.argv[0].lower() for arg in ['pytest', 'test']):
    app, metrics, request_count, request_latency, task_counter = create_app()

if __name__ == '__main__':
    app.run(host=app.config.get('HOST', '0.0.0.0'), port=app.config.get('PORT', 5000))
