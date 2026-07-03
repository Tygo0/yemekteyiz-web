import os
import sys
from flask import Flask, send_from_directory, abort
from config import config_by_name
from app.extensions import db, migrate, jwt, cors


def _resource_path(relative_path):
    """
    Resolves a path that works both when running normally (python3 wsgi.py)
    and when bundled by PyInstaller into a single executable. PyInstaller
    extracts bundled data files into a temp folder at runtime and exposes
    that location via sys._MEIPASS — a plain relative path would silently
    fail to find anything once frozen, since the working directory isn't
    the same as the source layout anymore.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__ + "/..")))
    return os.path.join(base, relative_path)


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    frontend_dist = _resource_path("frontend_dist")
    serve_frontend = os.path.isdir(frontend_dist)

    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db, directory=_resource_path("migrations"))
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

    if serve_frontend:
        # Single-process distribution: this Flask app serves both the API
        # (under /api/...) and the built React static files. The catch-all
        # route below implements the same "SPA fallback" that nginx.conf
        # would have done in a container setup — any path that isn't a real
        # static asset or an /api/ route falls back to index.html, so React
        # Router can handle client-side routes like /contestants directly.
        @app.get("/", defaults={"path": ""})
        @app.get("/<path:path>")
        def serve_react_app(path):
            # Never let the SPA fallback swallow unmatched /api/ requests —
            # those should fall through to Flask's normal JSON 404 handler
            # (registered above) instead of silently returning the
            # frontend's index.html with a false 200 status.
            if path.startswith("api/"):
                abort(404)
            full_path = os.path.join(frontend_dist, path)
            if path and os.path.isfile(full_path):
                return send_from_directory(frontend_dist, path)
            return send_from_directory(frontend_dist, "index.html")

    return app
