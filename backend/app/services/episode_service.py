from app.extensions import db
from app.models import Episode, Contestant
from app.utils.errors import NotFoundError


def list_episodes(contestant_id=None):
    query = Episode.query
    if contestant_id is not None:
        query = query.filter_by(contestant_id=contestant_id)
    return query.order_by(Episode.id).all()


def get_episode(episode_id):
    episode = db.session.get(Episode, episode_id)
    if not episode:
        raise NotFoundError(f"Episode {episode_id} not found")
    return episode


def create_episode(data):
    if not db.session.get(Contestant, data["contestant_id"]):
        raise NotFoundError(f"Contestant {data['contestant_id']} not found")
    episode = Episode(**data)
    db.session.add(episode)
    db.session.commit()
    return episode
