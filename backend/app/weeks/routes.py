from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.week_schema import WeekSchema, WeekUpdateSchema
from app.services import week_service

bp = Blueprint("weeks", __name__, url_prefix="/api/weeks")

schema = WeekSchema()
schema_many = WeekSchema(many=True)
update_schema = WeekUpdateSchema()


@bp.get("")
def list_weeks():
    return jsonify(schema_many.dump(week_service.list_weeks())), 200


@bp.get("/<int:week_id>")
def get_week(week_id):
    return jsonify(schema.dump(week_service.get_week(week_id))), 200


@bp.post("")
@jwt_required()
def create_week():
    data = schema.load(request.get_json(force=True) or {})
    week = week_service.create_week(data)
    return jsonify(schema.dump(week)), 201


@bp.put("/<int:week_id>")
@jwt_required()
def update_week(week_id):
    data = update_schema.load(request.get_json(force=True) or {}, partial=True)
    week = week_service.update_week(week_id, data)
    return jsonify(schema.dump(week)), 200


@bp.delete("/<int:week_id>")
@jwt_required()
def delete_week(week_id):
    week_service.delete_week(week_id)
    return "", 204
