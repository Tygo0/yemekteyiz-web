"""
Launcher for the packaged (PyInstaller) distribution — this is what the
bundled executable actually runs, NOT wsgi.py.

Unlike wsgi.py (used during development via `python3 wsgi.py` / `flask run` /
gunicorn, where you control .env, run migrations yourself, and seed an admin
manually), this script is meant to be double-clicked with zero setup:
  - auto-creates a local SQLite database next to the executable
  - runs migrations automatically (no `flask db upgrade` needed)
  - creates a default admin account on first run if one doesn't exist yet
  - starts a production-capable server (waitress — pure Python, works on
    Windows unlike gunicorn, which requires os.fork) and opens your browser
"""
import os
import sys
import secrets
import threading
import webbrowser


def _app_dir():
    """Directory the database/secret files live next to: the executable's
    own folder when frozen by PyInstaller, otherwise this script's folder
    during normal development. Using the executable's folder (not a temp
    extraction folder) matters here — PyInstaller onefile builds unpack to a
    new temp directory on every launch, so anything written there would be
    silently wiped between runs. The exe's own folder persists."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _ensure_secret_key(app_dir):
    """Generates a JWT signing secret once and persists it next to the exe.
    Without this, restarting the app would generate a new secret every time
    and silently invalidate every previously issued login token."""
    secret_path = os.path.join(app_dir, ".secret_key")
    if os.path.exists(secret_path):
        with open(secret_path) as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(secret_path, "w") as f:
        f.write(key)
    return key


def main():
    app_dir = _app_dir()
    db_path = os.path.join(app_dir, "yemekteyiz.db")

    os.environ.setdefault("DATABASE_URL", f"sqlite:///{db_path}")
    os.environ.setdefault("JWT_SECRET_KEY", _ensure_secret_key(app_dir))
    os.environ.setdefault("FLASK_ENV", "production")
    admin_username = os.environ.setdefault("ADMIN_USERNAME", "admin")
    admin_password = os.environ.setdefault("ADMIN_PASSWORD", "admin123")

    from app import create_app
    from app.extensions import db
    from app.models import Admin
    from flask_migrate import upgrade

    app = create_app()

    with app.app_context():
        upgrade()
        if not Admin.query.filter_by(username=admin_username).first():
            admin = Admin(username=admin_username)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Created admin account — username: {admin_username}  password: {admin_password}", flush=True)
            print("(Change this by setting ADMIN_USERNAME/ADMIN_PASSWORD before first launch.)", flush=True)
        else:
            print(f"Admin account '{admin_username}' already exists — using it as-is.", flush=True)

    port = int(os.environ.get("PORT", 5000))
    url = f"http://localhost:{port}"
    print(f"\nYemekteyiz is running at {url}", flush=True)
    print("Leave this window open while using the site. Press CTRL+C to stop.\n", flush=True)

    # Don't open a browser tab during automated tests / CI.
    if not os.environ.get("YEMEKTEYIZ_NO_BROWSER"):
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    from waitress import serve
    serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
