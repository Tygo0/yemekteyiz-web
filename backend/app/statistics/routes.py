from flask import Blueprint, jsonify
from app.services import statistics_service

bp = Blueprint("statistics", __name__, url_prefix="/api/statistics")


@bp.get("")
def get_statistics():
    return jsonify(statistics_service.get_all_statistics()), 200
