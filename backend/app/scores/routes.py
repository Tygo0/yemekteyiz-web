from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.score_schema import ScoreSchema, ScoreUpdateSchema
from app.services import score_service

bp = Blueprint("scores", __name__, url_prefix="/api/scores")

schema = ScoreSchema()
schema_many = ScoreSchema(many=True)
update_schema = ScoreUpdateSchema()


@bp.get("")
def list_scores():
    episode_id = request.args.get("episode_id", type=int)
    contestant_id = request.args.get("contestant_id", type=int)
    return jsonify(schema_many.dump(score_service.list_scores(episode_id, contestant_id))), 200


@bp.get("/<int:score_id>")
def get_score(score_id):
    return jsonify(schema.dump(score_service.get_score(score_id))), 200


@bp.post("")
@jwt_required()
def create_score():
    data = schema.load(request.get_json(force=True) or {})
    score = score_service.create_score(data)
    return jsonify(schema.dump(score)), 201


@bp.put("/<int:score_id>")
@jwt_required()
def update_score(score_id):
    data = update_schema.load(request.get_json(force=True) or {}, partial=True)
    score = score_service.update_score(score_id, data)
    return jsonify(schema.dump(score)), 200


@bp.delete("/<int:score_id>")
@jwt_required()
def delete_score(score_id):
    score_service.delete_score(score_id)
    return "", 204
