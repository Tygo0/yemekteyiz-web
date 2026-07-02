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

    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    from app.auth.routes import bp as auth_bp
    from app.seasons.routes import bp as seasons_bp
    from app.weeks.routes import bp as weeks_bp
    from app.contestants.routes import bp as contestants_bp
    from app.episodes.routes import bp as episodes_bp
    from app.dishes.routes import bp as dishes_bp
    from app.scores.routes import bp as scores_bp
    from app.statistics.routes import bp as statistics_bp
    from app.automation.routes import bp as automation_bp

    for bp in (
        auth_bp, seasons_bp, weeks_bp, contestants_bp, episodes_bp,
        dishes_bp, scores_bp, statistics_bp, automation_bp,
    ):
        app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
