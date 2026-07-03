from marshmallow import Schema, fields


class EpisodeSchema(Schema):
    id = fields.Int(dump_only=True)
    contestant_id = fields.Int(required=True)
    broadcast_date = fields.Date(required=False, allow_none=True)
    video_url = fields.Str(required=False, allow_none=True)


class EpisodeUpdateSchema(Schema):
    broadcast_date = fields.Date(allow_none=True)
    video_url = fields.Str(allow_none=True)
