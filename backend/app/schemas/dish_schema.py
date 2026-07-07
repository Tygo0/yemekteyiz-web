from marshmallow import Schema, fields, validate, ValidationError
from app.models import DishCategory

VALID_CATEGORIES = [c.value for c in DishCategory]


class DishCategoryField(fields.Field):
    """
    Dish.category is stored as a DishCategory enum (SQLAlchemy db.Enum column),
    so a plain fields.Str would dump Python's default enum repr
    ("DishCategory.SOUP") instead of the plain value ("soup") the frontend
    and API consumers actually expect. Serializes to .value; still validates
    incoming strings against the same allowed values on load.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value if isinstance(value, DishCategory) else value

    def _deserialize(self, value, attr, data, **kwargs):
        if value not in VALID_CATEGORIES:
            raise ValidationError(f"Must be one of: {VALID_CATEGORIES}.")
        return value


class DishSchema(Schema):
    id = fields.Int(dump_only=True)
    episode_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    category = DishCategoryField(required=True)


class DishUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    category = DishCategoryField()
