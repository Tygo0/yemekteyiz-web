from marshmallow import Schema, fields, validate
from app.models import DishCategory

VALID_CATEGORIES = [c.value for c in DishCategory]


class AutomationDishSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    category = fields.Str(required=True, validate=validate.OneOf(VALID_CATEGORIES))


class AutomationScoreSchema(Schema):
    judge_name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    value = fields.Int(required=True, validate=validate.Range(min=1, max=10))


class AutomationContestantSchema(Schema):
    # Automation identifies contestants by name (parsed from video), not by
    # DB id — the service layer matches against existing contestants for the
    # week, or creates a new one if no name match is found.
    name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    age = fields.Int(required=False, allow_none=True, validate=validate.Range(min=0, max=120))
    profession = fields.Str(required=False, allow_none=True, validate=validate.Length(max=150))
    city = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    biography = fields.Str(required=False, allow_none=True)
    photo_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    broadcast_date = fields.Date(required=False, allow_none=True)
    video_url = fields.Str(required=False, allow_none=True)
    dishes = fields.List(fields.Nested(AutomationDishSchema), required=False, load_default=list)
    scores = fields.List(fields.Nested(AutomationScoreSchema), required=False, load_default=list)


class AutomationImportSchema(Schema):
    week_id = fields.Int(required=True)
    # The blueprint's validation gate expects exactly four contestants per
    # week/episode — enforced here at the field level (not just in the
    # automation pipeline's own validator) so a malformed request is rejected
    # even if it reaches the backend directly.
    contestants = fields.List(
        fields.Nested(AutomationContestantSchema),
        required=True,
        validate=validate.Length(equal=4),
    )


class AutomationFailureReportSchema(Schema):
    # Lets the automation pipeline log a failure it caught on its own side
    # (e.g. its client-side validator rejecting a payload, or the vision
    # stage refusing to fabricate data for an irrelevant video) BEFORE ever
    # building a full /automation/import payload — otherwise those failures
    # would be invisible to GET /automation/logs entirely, since they never
    # reach the backend at all today.
    week_id = fields.Int(required=True)
    error_message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    contestant_count = fields.Int(required=False, load_default=0)


class AutomationImportLogSchema(Schema):
    id = fields.Int(dump_only=True)
    week_id = fields.Int(dump_only=True)
    status = fields.Method("get_status", dump_only=True)
    contestant_count = fields.Int(dump_only=True)
    error_message = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)

    def get_status(self, obj):
        return obj.status.value
