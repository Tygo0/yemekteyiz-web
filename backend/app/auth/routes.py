from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.auth_schema import LoginSchema
from app.services import auth_service

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

login_schema = LoginSchema()


@bp.post("/login")
def login():
    data = login_schema.load(request.get_json(force=True) or {})
    result = auth_service.authenticate(data["username"], data["password"])
    return jsonify(result), 200


@bp.post("/logout")
@jwt_required()
def logout():
    # Stateless JWTs: "logout" is a client-side action (discard the token).
    # This endpoint exists for API symmetry / future token-blocklist support.
    return jsonify({"message": "Logged out"}), 200


@bp.get("/me")
@jwt_required()
def me():
    admin = auth_service.get_current_admin(get_jwt_identity())
    return jsonify({"id": admin.id, "username": admin.username}), 200
