import os
from flask import Flask
from config import config_by_name
from app.extensions import db, migrate, jwt, cors


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # Import models so they're registered with SQLAlchemy's metadata before
    # migrations run.
    from app import models  # noqa: F401

    # Blueprints are registered here as each feature module gets built out
    # in later phases (auth, contestants, weeks, episodes, dishes, scores,
    # statistics, automation).

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
