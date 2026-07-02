from app.extensions import db
from app.models import Dish, DishCategory, Episode
from app.utils.errors import NotFoundError


def list_dishes(episode_id=None):
    query = Dish.query
    if episode_id is not None:
        query = query.filter_by(episode_id=episode_id)
    return query.order_by(Dish.id).all()


def get_dish(dish_id):
    dish = db.session.get(Dish, dish_id)
    if not dish:
        raise NotFoundError(f"Dish {dish_id} not found")
    return dish


def create_dish(data):
    if not db.session.get(Episode, data["episode_id"]):
        raise NotFoundError(f"Episode {data['episode_id']} not found")
    data = {**data, "category": DishCategory(data["category"])}
    dish = Dish(**data)
    db.session.add(dish)
    db.session.commit()
    return dish


def update_dish(dish_id, data):
    dish = get_dish(dish_id)
    if "category" in data:
        data["category"] = DishCategory(data["category"])
    for key, value in data.items():
        setattr(dish, key, value)
    db.session.commit()
    return dish


def delete_dish(dish_id):
    dish = get_dish(dish_id)
    db.session.delete(dish)
    db.session.commit()
