from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.dish_schema import DishSchema, DishUpdateSchema
from app.services import dish_service

bp = Blueprint("dishes", __name__, url_prefix="/api/dishes")

schema = DishSchema()
schema_many = DishSchema(many=True)
update_schema = DishUpdateSchema()


@bp.get("")
def list_dishes():
    episode_id = request.args.get("episode_id", type=int)
    return jsonify(schema_many.dump(dish_service.list_dishes(episode_id))), 200


@bp.get("/<int:dish_id>")
def get_dish(dish_id):
    return jsonify(schema.dump(dish_service.get_dish(dish_id))), 200


@bp.post("")
@jwt_required()
def create_dish():
    data = schema.load(request.get_json(force=True) or {})
    dish = dish_service.create_dish(data)
    return jsonify(schema.dump(dish)), 201


@bp.put("/<int:dish_id>")
@jwt_required()
def update_dish(dish_id):
    data = update_schema.load(request.get_json(force=True) or {}, partial=True)
    dish = dish_service.update_dish(dish_id, data)
    return jsonify(schema.dump(dish)), 200


@bp.delete("/<int:dish_id>")
@jwt_required()
def delete_dish(dish_id):
    dish_service.delete_dish(dish_id)
    return "", 204
