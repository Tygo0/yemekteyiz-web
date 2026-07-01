"""
Shared Flask extension instances.

Defined here (not inside app/__init__.py) so that models.py and other modules
can `from app.extensions import db` without triggering circular imports with
the app factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
