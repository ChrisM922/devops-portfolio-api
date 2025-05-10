from flask import Flask
from app.config import Config
from app.database import db  # ✅ correct import


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from app.routes import register_routes  # delay route import
    register_routes(app)

    return app
