from sqlalchemy import func
from app.extensions import db
from app.models import Week, Contestant, Episode, Dish, Score


def weekly_winners():
    """Every week that has a winner set, with the winner's name."""
    rows = (
        db.session.query(Week, Contestant)
        .join(Contestant, Week.winner_id == Contestant.id)
        .order_by(Week.season_id, Week.week_number)
        .all()
    )
    return [
        {
            "week_id": week.id,
            "season_id": week.season_id,
            "week_number": week.week_number,
            "winner_id": winner.id,
            "winner_name": winner.name,
        }
        for week, winner in rows
    ]


def average_score():
    result = db.session.query(func.avg(Score.value)).scalar()
    return round(float(result), 2) if result is not None else None


def highest_score_ever():
    row = (
        db.session.query(Score, Contestant)
        .join(Contestant, Score.contestant_id == Contestant.id)
        .order_by(Score.value.desc())
        .first()
    )
    if not row:
        return None
    score, contestant = row
    return {
        "score_id": score.id,
        "value": score.value,
        "contestant_id": contestant.id,
        "contestant_name": contestant.name,
        "judge_name": score.judge_name,
    }


def most_common_dish():
    row = (
        db.session.query(Dish.name, func.count(Dish.id).label("count"))
        .group_by(Dish.name)
        .order_by(func.count(Dish.id).desc())
        .first()
    )
    if not row:
        return None
    return {"dish_name": row.name, "count": row.count}


def most_successful_contestant():
    """Contestant with the highest average score across all their episodes."""
    row = (
        db.session.query(
            Contestant.id, Contestant.name, func.avg(Score.value).label("avg_score")
        )
        .join(Score, Score.contestant_id == Contestant.id)
        .group_by(Contestant.id, Contestant.name)
        .order_by(func.avg(Score.value).desc())
        .first()
    )
    if not row:
        return None
    return {
        "contestant_id": row.id,
        "contestant_name": row.name,
        "average_score": round(float(row.avg_score), 2),
    }


def average_weekly_score():
    """Average score per week, across all episodes/contestants in that week."""
    rows = (
        db.session.query(
            Week.id, Week.week_number, func.avg(Score.value).label("avg_score")
        )
        .join(Contestant, Contestant.week_id == Week.id)
        .join(Episode, Episode.contestant_id == Contestant.id)
        .join(Score, Score.episode_id == Episode.id)
        .group_by(Week.id, Week.week_number)
        .order_by(Week.week_number)
        .all()
    )
    return [
        {
            "week_id": r.id,
            "week_number": r.week_number,
            "average_score": round(float(r.avg_score), 2),
        }
        for r in rows
    ]


def score_distribution():
    """Count of scores at each value 1-10, useful for a histogram on the frontend.
    Keys are strings (not ints) because JSON object keys are always strings —
    returning int keys here would work in Python but silently become "1".."10"
    after jsonify(), which is a common source of frontend bugs if untested."""
    rows = (
        db.session.query(Score.value, func.count(Score.id).label("count"))
        .group_by(Score.value)
        .order_by(Score.value)
        .all()
    )
    counts = {str(v): 0 for v in range(1, 11)}
    for value, count in rows:
        counts[str(value)] = count
    return counts


def get_all_statistics():
    return {
        "weekly_winners": weekly_winners(),
        "average_score": average_score(),
        "highest_score_ever": highest_score_ever(),
        "most_common_dish": most_common_dish(),
        "most_successful_contestant": most_successful_contestant(),
        "average_weekly_score": average_weekly_score(),
        "score_distribution": score_distribution(),
    }
