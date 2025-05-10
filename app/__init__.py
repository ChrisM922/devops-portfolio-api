from flask import Flask, jsonify
from app.config import Config
from app.database import db
from app.models import Task  # Import the Task model
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    db.init_app(app)

    with app.app_context():
        try:
            # Drop all tables first (in development)
            if app.config.get('FLASK_ENV') == 'development':
                db.drop_all()
            
            # Create all tables
            db.create_all()
            
            # Verify table exists
            if not db.engine.dialect.has_table(db.engine, 'task'):
                app.logger.error("Task table was not created!")
                raise Exception("Database initialization failed")
                
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise

    from app.routes import register_routes
    register_routes(app)

    # Error handlers
    @app.errorhandler(500)
    def handle_500_error(e):
        app.logger.error(f"500 error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({"error": "Not found"}), 404

    return app
