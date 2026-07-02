"""
Centralized error handling.

Services raise AppError for expected business-rule failures (not found, conflict,
invalid state). Routes never need their own try/except for these — the app-wide
handler registered in register_error_handlers() converts them to JSON responses.
Marshmallow ValidationError is handled the same way so every schema-validation
failure returns a consistent 400 shape.
"""
from flask import jsonify
from marshmallow import ValidationError


class AppError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        d = dict(self.payload)
        d["error"] = self.message
        return d


class NotFoundError(AppError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(AppError):
    def __init__(self, message="Conflict"):
        super().__init__(message, status_code=409)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def handle_405(err):
        return jsonify({"error": "Method not allowed"}), 405
