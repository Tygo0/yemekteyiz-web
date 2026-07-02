"""
Creates the first admin user, reading credentials from environment variables.

Usage:
    ADMIN_USERNAME=admin ADMIN_PASSWORD=changeme python3 seed.py
"""
import os
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
