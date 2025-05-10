from app.database import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import validates


class Task(db.Model):
    __tablename__ = 'task'  # Explicitly set table name
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, title, description=None):
        if not isinstance(title, str):
            raise ValueError("Title must be a string")
        self.title = title
        self.description = description

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
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'done': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
