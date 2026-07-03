from marshmallow import Schema, fields, validate


class SeasonSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    year = fields.Int(required=True, validate=validate.Range(min=2000, max=2100))


class SeasonUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=100))
    year = fields.Int(validate=validate.Range(min=2000, max=2100))
