from marshmallow import Schema, fields, validate


class ScoreSchema(Schema):
    id = fields.Int(dump_only=True)
    episode_id = fields.Int(required=True)
    contestant_id = fields.Int(required=True)
    judge_name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    # Mirrors the DB CHECK constraint (value BETWEEN 1 AND 10) so bad input is
    # rejected with a clear 400 message before it ever reaches the database.
    value = fields.Int(required=True, validate=validate.Range(min=1, max=10))
