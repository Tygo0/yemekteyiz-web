from marshmallow import Schema, fields, validate


class ContestantSchema(Schema):
    id = fields.Int(dump_only=True)
    week_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    age = fields.Int(required=False, allow_none=True, validate=validate.Range(min=0, max=120))
    profession = fields.Str(required=False, allow_none=True, validate=validate.Length(max=150))
    city = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    biography = fields.Str(required=False, allow_none=True)
    photo_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))


class ContestantUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=150))
    age = fields.Int(allow_none=True, validate=validate.Range(min=0, max=120))
    profession = fields.Str(allow_none=True, validate=validate.Length(max=150))
    city = fields.Str(allow_none=True, validate=validate.Length(max=100))
    biography = fields.Str(allow_none=True)
    photo_url = fields.Str(allow_none=True, validate=validate.Length(max=500))
