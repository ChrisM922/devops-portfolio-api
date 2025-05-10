from datetime import datetime
from app.database import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import validates


class Task(db.Model):
    """Task model for storing task items."""
    __tablename__ = 'task'  # Explicitly set table name
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    done = db.Column(db.Boolean, default=False)
    
    # Make timestamp fields nullable
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Task {self.title}>'

    def __init__(self, title, description=None):
        if not isinstance(title, str):
            raise ValueError("Title must be a string")
        self.title = title
        self.description = description
        # Initialize timestamps here in case the DB doesn't have these columns
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @validates('title')
    def validate_title(self, key, title):
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a string")
        if not title.strip():
            raise ValueError("Title cannot be empty")
        if len(title) > 100:
            raise ValueError("Title cannot be longer than 100 characters")
        return title.strip()

    def to_dict(self):
        """Convert task to dictionary."""
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description or '',
            'done': self.done
        }
        # Only add timestamp fields if they exist
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            result['updated_at'] = self.updated_at.isoformat()
        return result
