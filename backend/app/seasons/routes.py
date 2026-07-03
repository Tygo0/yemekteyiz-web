from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.season_schema import SeasonSchema, SeasonUpdateSchema
from app.services import season_service

bp = Blueprint("seasons", __name__, url_prefix="/api/seasons")

schema = SeasonSchema()
schema_many = SeasonSchema(many=True)
update_schema = SeasonUpdateSchema()


@bp.get("")
def list_seasons():
    return jsonify(schema_many.dump(season_service.list_seasons())), 200


@bp.get("/<int:season_id>")
def get_season(season_id):
    return jsonify(schema.dump(season_service.get_season(season_id))), 200


@bp.post("")
@jwt_required()
def create_season():
    data = schema.load(request.get_json(force=True) or {})
    season = season_service.create_season(data)
    return jsonify(schema.dump(season)), 201


@bp.put("/<int:season_id>")
@jwt_required()
def update_season(season_id):
    data = update_schema.load(request.get_json(force=True) or {}, partial=True)
    season = season_service.update_season(season_id, data)
    return jsonify(schema.dump(season)), 200
