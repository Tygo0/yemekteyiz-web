from marshmallow import Schema, fields, validate
from app.models import DishCategory

VALID_CATEGORIES = [c.value for c in DishCategory]


class DishSchema(Schema):
    id = fields.Int(dump_only=True)
    episode_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    category = fields.Str(required=True, validate=validate.OneOf(VALID_CATEGORIES))


class DishUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    category = fields.Str(validate=validate.OneOf(VALID_CATEGORIES))
