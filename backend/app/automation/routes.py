"""
Automation endpoints exist now to match the blueprint's REST API design, but are
intentionally stubbed — the real AI pipeline (downloader/ocr/vision/speech/parser/
validator) is built in Phase 6. Per the engineering principle "build the manual
management system completely before implementing AI automation," these just
acknowledge requests for now.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

bp = Blueprint("automation", __name__, url_prefix="/api/automation")


@bp.post("/import")
@jwt_required()
def trigger_import():
    return jsonify({
        "status": "not_implemented",
        "message": "Automation pipeline is built in Phase 6. This endpoint is a placeholder.",
    }), 501


@bp.get("/status")
def automation_status():
    return jsonify({"status": "idle", "note": "Automation pipeline not yet implemented (Phase 6)"}), 200


@bp.get("/logs")
def automation_logs():
    return jsonify({"logs": [], "note": "Automation pipeline not yet implemented (Phase 6)"}), 200
