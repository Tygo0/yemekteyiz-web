from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.episode_schema import EpisodeSchema, EpisodeUpdateSchema
from app.services import episode_service

bp = Blueprint("episodes", __name__, url_prefix="/api/episodes")

schema = EpisodeSchema()
schema_many = EpisodeSchema(many=True)
update_schema = EpisodeUpdateSchema()


@bp.get("")
def list_episodes():
    contestant_id = request.args.get("contestant_id", type=int)
    return jsonify(schema_many.dump(episode_service.list_episodes(contestant_id))), 200


@bp.get("/<int:episode_id>")
def get_episode(episode_id):
    return jsonify(schema.dump(episode_service.get_episode(episode_id))), 200


@bp.post("")
@jwt_required()
def create_episode():
    data = schema.load(request.get_json(force=True) or {})
    episode = episode_service.create_episode(data)
    return jsonify(schema.dump(episode)), 201


@bp.put("/<int:episode_id>")
@jwt_required()
def update_episode(episode_id):
    data = update_schema.load(request.get_json(force=True) or {}, partial=True)
    episode = episode_service.update_episode(episode_id, data)
    return jsonify(schema.dump(episode)), 200


@bp.delete("/<int:episode_id>")
@jwt_required()
def delete_episode(episode_id):
    episode_service.delete_episode(episode_id)
    return "", 204
