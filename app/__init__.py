import os
from flask import Flask
from .models import db


def create_app():
    """
    Flask application factory.

    Tier 2 (Application Layer): creates and configures the Flask app,
    connects it to the SQLite database, and registers the route blueprint.
    """
    app = Flask(__name__)

    # ── Configuration ─────────────────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "weather_app.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "cs3720-weather-secret"

    # ── Initialize extensions ─────────────────────────────────────────────────
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Create SQLite tables if they don't exist yet

    # ── Register blueprint ────────────────────────────────────────────────────
    from .routes import main
    app.register_blueprint(main)

    return app
