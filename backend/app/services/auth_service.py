from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import Admin
from app.utils.errors import AppError


def authenticate(username, password):
    admin = Admin.query.filter_by(username=username).first()
    if not admin or not admin.check_password(password):
        raise AppError("Invalid username or password", status_code=401)

    token = create_access_token(identity=str(admin.id))
    return {"access_token": token, "admin": {"id": admin.id, "username": admin.username}}


def get_current_admin(admin_id):
    admin = db.session.get(Admin, int(admin_id))
    if not admin:
        raise AppError("Admin not found", status_code=404)
    return admin
