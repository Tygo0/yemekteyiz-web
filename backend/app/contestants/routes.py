from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.contestant_schema import ContestantSchema, ContestantUpdateSchema
from app.services import contestant_service

bp = Blueprint("contestants", __name__, url_prefix="/api/contestants")

schema = ContestantSchema()
schema_many = ContestantSchema(many=True)
update_schema = ContestantUpdateSchema()


@bp.get("")
def list_contestants():
    week_id = request.args.get("week_id", type=int)
    return jsonify(schema_many.dump(contestant_service.list_contestants(week_id))), 200


@bp.get("/<int:contestant_id>")
def get_contestant(contestant_id):
    return jsonify(schema.dump(contestant_service.get_contestant(contestant_id))), 200


@bp.post("")
@jwt_required()
def create_contestant():
    data = schema.load(request.get_json(force=True) or {})
    contestant = contestant_service.create_contestant(data)
    return jsonify(schema.dump(contestant)), 201


@bp.put("/<int:contestant_id>")
@jwt_required()
def update_contestant(contestant_id):
    data = update_schema.load(request.get_json(force=True) or {}, partial=True)
    contestant = contestant_service.update_contestant(contestant_id, data)
    return jsonify(schema.dump(contestant)), 200


@bp.delete("/<int:contestant_id>")
@jwt_required()
def delete_contestant(contestant_id):
    contestant_service.delete_contestant(contestant_id)
    return "", 204
