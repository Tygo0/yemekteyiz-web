from flask import Blueprint, jsonify
from app.services import statistics_service

bp = Blueprint("statistics", __name__, url_prefix="/api/statistics")


@bp.get("")
def get_statistics():
    return jsonify(statistics_service.get_all_statistics()), 200


@bp.get("/vote-matrix/<int:week_id>")
def get_vote_matrix(week_id):
    return jsonify(statistics_service.vote_matrix(week_id)), 200
