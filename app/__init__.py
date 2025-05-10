import os
from flask import Flask, jsonify, make_response
from prometheus_client import Counter, make_wsgi_app, REGISTRY
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app.database import db
import logging

def create_app(config=None, registry=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    
    # Ensure logger has a handler
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Override with passed config
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Create Prometheus metrics
    if registry is not None:
        # Clear any existing metrics with the same names
        for metric_name in ['task_operations_total', 'task_operations', 'task_operations_created']:
            if metric_name in registry._names_to_collectors:
                del registry._names_to_collectors[metric_name]
        
        app.metrics = {
            'task_operations': Counter('task_operations_total', 
                                     'Total task operations', 
                                     ['operation'],
                                     registry=registry)
        }
        # Add Prometheus WSGI middleware
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
            '/metrics': make_wsgi_app(registry=registry)
        })
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return make_response(
            jsonify({"error": "Resource not found"}),
            404,
            {'Content-Type': 'application/json'}
        )

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 Method Not Allowed errors."""
        return make_response(
            jsonify({"error": "Method not allowed"}),
            405,
            {'Content-Type': 'application/json'}
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return make_response(
            jsonify({"error": "Internal server error"}),
            500,
            {'Content-Type': 'application/json'}
        )

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {str(error)}")
        return make_response(
            jsonify({"error": "Internal server error"}),
            500,
            {'Content-Type': 'application/json'}
        )
    
    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    return app

# This file makes the app directory a Python package
