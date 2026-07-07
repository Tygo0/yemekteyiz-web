"""
Automation import endpoint: the one place the AI pipeline (built out under the
top-level automation/ package) talks to the backend. Per the architecture's
hard rule, the automation service never touches SQL directly — it POSTs
structured JSON here and the existing contestant/episode/dish/score services
own validation and persistence, exactly like a human admin's requests would.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.automation_schema import AutomationImportSchema
from app.schemas.contestant_schema import ContestantSchema
from app.schemas.episode_schema import EpisodeSchema
from app.schemas.dish_schema import DishSchema
from app.schemas.score_schema import ScoreSchema
from app.services import automation_service

bp = Blueprint("automation", __name__, url_prefix="/api/automation")

import_schema = AutomationImportSchema()
contestant_schema = ContestantSchema()
episode_schema = EpisodeSchema()
dish_schema = DishSchema(many=True)
score_schema = ScoreSchema(many=True)


@bp.post("/import")
@jwt_required()
def trigger_import():
    data = import_schema.load(request.get_json(force=True) or {})
    created = automation_service.import_week(data)
    return jsonify({
        "status": "imported",
        "week_id": data["week_id"],
        "contestants": [
            {
                "contestant": contestant_schema.dump(entry["contestant"]),
                "episode": episode_schema.dump(entry["episode"]),
                "dishes": dish_schema.dump(entry["dishes"]),
                "scores": score_schema.dump(entry["scores"]),
            }
            for entry in created
        ],
    }), 201


@bp.get("/status")
def automation_status():
    return jsonify({"status": "idle", "note": "Pipeline runs on demand via the automation/ package; no background scheduler is running yet"}), 200


@bp.get("/logs")
def automation_logs():
    return jsonify({"logs": [], "note": "Structured import logging not yet implemented"}), 200
