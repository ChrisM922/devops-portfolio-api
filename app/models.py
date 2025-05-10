from app.database import db
from flask_sqlalchemy import SQLAlchemy

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256))
    done = db.Column(db.Boolean, default=False)
