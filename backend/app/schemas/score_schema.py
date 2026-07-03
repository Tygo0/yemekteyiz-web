from marshmallow import Schema, fields, validate


class ScoreSchema(Schema):
    id = fields.Int(dump_only=True)
    episode_id = fields.Int(required=True)
    contestant_id = fields.Int(required=True)
    judge_name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    # Mirrors the DB CHECK constraint (value BETWEEN 1 AND 10) so bad input is
    # rejected with a clear 400 message before it ever reaches the database.
    value = fields.Int(required=True, validate=validate.Range(min=1, max=10))


class ScoreUpdateSchema(Schema):
    # episode_id/contestant_id are intentionally excluded — changing which
    # episode or contestant a score belongs to should be a delete + re-create,
    # not an edit, so the create-time contestant/episode match validation
    # can't be silently bypassed by an update.
    judge_name = fields.Str(validate=validate.Length(min=1, max=150))
    value = fields.Int(validate=validate.Range(min=1, max=10))
