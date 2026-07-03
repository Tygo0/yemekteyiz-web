from app.extensions import db
from app.models import Score, Episode, Contestant
from app.utils.errors import NotFoundError, AppError


def list_scores(episode_id=None, contestant_id=None):
    query = Score.query
    if episode_id is not None:
        query = query.filter_by(episode_id=episode_id)
    if contestant_id is not None:
        query = query.filter_by(contestant_id=contestant_id)
    return query.order_by(Score.id).all()


def get_score(score_id):
    score = db.session.get(Score, score_id)
    if not score:
        raise NotFoundError(f"Score {score_id} not found")
    return score


def create_score(data):
    episode = db.session.get(Episode, data["episode_id"])
    if not episode:
        raise NotFoundError(f"Episode {data['episode_id']} not found")

    contestant = db.session.get(Contestant, data["contestant_id"])
    if not contestant:
        raise NotFoundError(f"Contestant {data['contestant_id']} not found")

    # A score for an episode must be scoring the contestant that episode
    # actually belongs to — catches an obvious mismatched-ID bug in either a
    # human admin's request or the AI automation pipeline's parsed output.
    if contestant.id != episode.contestant_id:
        raise AppError(
            "Contestant does not match the episode's contestant", status_code=400
        )

    score = Score(**data)
    db.session.add(score)
    db.session.commit()
    return score


def update_score(score_id, data):
    score = get_score(score_id)
    for key, value in data.items():
        setattr(score, key, value)
    db.session.commit()
    return score


def delete_score(score_id):
    score = get_score(score_id)
    db.session.delete(score)
    db.session.commit()
