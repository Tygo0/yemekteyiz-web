from marshmallow import Schema, fields, validate


class WeekSchema(Schema):
    id = fields.Int(dump_only=True)
    season_id = fields.Int(required=True)
    week_number = fields.Int(required=True, validate=validate.Range(min=1))
    air_date = fields.Date(required=False, allow_none=True)
    youtube_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    winner_id = fields.Int(required=False, allow_none=True)
    notes = fields.Str(required=False, allow_none=True)


class WeekUpdateSchema(Schema):
    """Separate schema for PUT: every field optional, still validated if present."""

    week_number = fields.Int(validate=validate.Range(min=1))
    air_date = fields.Date(allow_none=True)
    youtube_url = fields.Str(allow_none=True, validate=validate.Length(max=500))
    winner_id = fields.Int(allow_none=True)
    notes = fields.Str(allow_none=True)
