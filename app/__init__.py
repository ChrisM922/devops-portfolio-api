import logging
from flask import Flask, jsonify
from app.config import Config
from app.database import db
from app.models import Task

def create_app(config_object=None):
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)
    
    # Ensure database URI is set
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        try:
            # Drop all tables first (in development)
            if app.config.get('FLASK_ENV') == 'development':
                db.drop_all()
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    # Register routes
    from app.routes import register_routes
    register_routes(app)
    
    # Error handlers
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {str(error)}")
        return jsonify({"error": "Resource not found"}), 404
    
    return app

# This file makes the app directory a Python package 