from sqlalchemy import func
from app.extensions import db
from app.models import Week, Contestant, Episode, Dish, Score
from app.services import week_service


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


def vote_matrix(week_id):
    """
    Who gave points to whom, for one week. Rows are that week's contestants;
    columns are every distinct judge who actually scored that week — whether
    that's named external judges (e.g. the host), contestants scoring each
    other (a Score whose judge_name happens to match one of that week's
    contestants), or both. No column is hardcoded, since which judges exist
    varies by week/season rather than being a fixed roster.
    """
    week_service.get_week(week_id)  # raises NotFoundError if the week doesn't exist

    contestants = Contestant.query.filter_by(week_id=week_id).order_by(Contestant.id).all()
    contestant_ids = [c.id for c in contestants]

    scores = (
        db.session.query(Score)
        .join(Episode, Score.episode_id == Episode.id)
        .filter(Episode.contestant_id.in_(contestant_ids))
        .all()
        if contestant_ids
        else []
    )

    judges = sorted({s.judge_name for s in scores})

    matrix = {str(c.id): {} for c in contestants}
    for s in scores:
        matrix[str(s.contestant_id)][s.judge_name] = s.value

    return {
        "week_id": week_id,
        "contestants": [{"id": c.id, "name": c.name} for c in contestants],
        "judges": judges,
        "matrix": matrix,
    }


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
