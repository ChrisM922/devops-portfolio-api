from flask import Flask, jsonify
from app.config import Config
from app.database import db  # ✅ correct import
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
            db.create_all()  # Create database tables
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise

    from app.routes import register_routes  # delay route import
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
