from app.extensions import db
from app.models import Season
from app.utils.errors import NotFoundError


def list_seasons():
    return Season.query.order_by(Season.year.desc()).all()


def get_season(season_id):
    season = db.session.get(Season, season_id)
    if not season:
        raise NotFoundError(f"Season {season_id} not found")
    return season


def create_season(data):
    season = Season(**data)
    db.session.add(season)
    db.session.commit()
    return season


def update_season(season_id, data):
    season = get_season(season_id)
    for key, value in data.items():
        setattr(season, key, value)
    db.session.commit()
    return season
