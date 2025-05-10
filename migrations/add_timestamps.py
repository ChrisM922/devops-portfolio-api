from app import create_app
from app.database import db
from sqlalchemy import text
import logging

logger = logging.getLogger('migrations')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def run_migration():
    """Add timestamp columns to task table if they don't exist."""
    logger.info("Starting migration: Adding timestamp columns to task table")
    
    # Get the Flask app
    app_instance, _, _, _, _ = create_app()
    
    with app_instance.app_context():
        try:
            # Check if columns exist
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'task' AND column_name = 'created_at'"))
            has_created_at = result.scalar() is not None
            
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'task' AND column_name = 'updated_at'"))
            has_updated_at = result.scalar() is not None
            
            # Add columns if they don't exist
            if not has_created_at:
                logger.info("Adding created_at column to task table")
                db.session.execute(text("ALTER TABLE task ADD COLUMN created_at TIMESTAMP"))
                
            if not has_updated_at:
                logger.info("Adding updated_at column to task table")
                db.session.execute(text("ALTER TABLE task ADD COLUMN updated_at TIMESTAMP"))
                
            if not has_created_at or not has_updated_at:
                db.session.commit()
                logger.info("Migration completed successfully")
            else:
                logger.info("No migration needed, columns already exist")
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration() 