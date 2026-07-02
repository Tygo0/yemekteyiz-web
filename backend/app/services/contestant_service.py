from app.extensions import db
from app.models import Contestant, Week
from app.utils.errors import NotFoundError


def list_contestants(week_id=None):
    query = Contestant.query
    if week_id is not None:
        query = query.filter_by(week_id=week_id)
    return query.order_by(Contestant.id).all()


def get_contestant(contestant_id):
    contestant = db.session.get(Contestant, contestant_id)
    if not contestant:
        raise NotFoundError(f"Contestant {contestant_id} not found")
    return contestant


def create_contestant(data):
    if not db.session.get(Week, data["week_id"]):
        raise NotFoundError(f"Week {data['week_id']} not found")
    contestant = Contestant(**data)
    db.session.add(contestant)
    db.session.commit()
    return contestant


def update_contestant(contestant_id, data):
    contestant = get_contestant(contestant_id)
    for key, value in data.items():
        setattr(contestant, key, value)
    db.session.commit()
    return contestant


def delete_contestant(contestant_id):
    contestant = get_contestant(contestant_id)
    db.session.delete(contestant)
    db.session.commit()
