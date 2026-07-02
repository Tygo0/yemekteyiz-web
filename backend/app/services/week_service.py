from app.extensions import db
from app.models import Week, Contestant, Season
from app.utils.errors import NotFoundError, ConflictError, AppError


def list_weeks():
    return Week.query.order_by(Week.season_id, Week.week_number).all()


def get_week(week_id):
    week = db.session.get(Week, week_id)
    if not week:
        raise NotFoundError(f"Week {week_id} not found")
    return week


def create_week(data):
    if not db.session.get(Season, data["season_id"]):
        raise NotFoundError(f"Season {data['season_id']} not found")

    existing = Week.query.filter_by(
        season_id=data["season_id"], week_number=data["week_number"]
    ).first()
    if existing:
        raise ConflictError(
            f"Week {data['week_number']} already exists for season {data['season_id']}"
        )

    week = Week(**data)
    db.session.add(week)
    db.session.commit()
    return week


def update_week(week_id, data):
    week = get_week(week_id)

    if "winner_id" in data and data["winner_id"] is not None:
        winner = db.session.get(Contestant, data["winner_id"])
        if not winner:
            raise NotFoundError(f"Contestant {data['winner_id']} not found")
        if winner.week_id != week.id:
            raise AppError(
                "Winner must be a contestant belonging to this week", status_code=400
            )

    for key, value in data.items():
        setattr(week, key, value)
    db.session.commit()
    return week


def delete_week(week_id):
    week = get_week(week_id)
    db.session.delete(week)
    db.session.commit()
