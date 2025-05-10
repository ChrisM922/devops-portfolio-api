import os
import logging
from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import CollectorRegistry
from app.config import Config
from app.database import db

def create_app(config_class=Config):
    app = Flask(__name__)
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
    
    # Initialize Prometheus metrics
    registry = app.config.get('PROMETHEUS_REGISTRY', CollectorRegistry())
    metrics = PrometheusMetrics(app, registry=registry)
    metrics.info('app_info', 'Application info', version='1.0.0')

    # Register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Create all database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
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

    return app

# This file makes the app directory a Python package
