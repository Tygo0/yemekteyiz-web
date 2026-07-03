"""
Creates the first admin user, reading credentials from environment variables.

Usage:
    ADMIN_USERNAME=admin ADMIN_PASSWORD=changeme python3 seed.py
"""
import os
from dotenv import load_dotenv

# Explicit load, not implicit: python-dotenv's automatic .env discovery only
# kicks in for the `flask` CLI command (e.g. `flask db upgrade`). This script
# is run as a plain `python3 seed.py`, which python-dotenv does NOT auto-load
# for — without this line, DATABASE_URL etc. from .env would be silently
# ignored and the app would fall back to config.py's hardcoded default.
load_dotenv()

from app import create_app
from app.extensions import db
from app.models import Admin


def seed_admin():
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD")
    if not password:
        raise SystemExit("Set ADMIN_PASSWORD before running the seed script.")

    app = create_app()
    with app.app_context():
        if Admin.query.filter_by(username=username).first():
            print(f"Admin '{username}' already exists — skipping.")
            return
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin '{username}'.")


if __name__ == "__main__":
    seed_admin()
