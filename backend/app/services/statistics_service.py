from sqlalchemy import func
from app.extensions import db
from app.models import Week, Contestant, Episode, Dish, Score
from app.services import week_service


def weekly_winners():
    """Every week that has at least one winner set, with all winners' names —
    a week can have more than one (a tie), since winner status lives on
    Contestant.is_winner rather than a single Week.winner_id."""
    rows = (
        db.session.query(Week, Contestant)
        .join(Contestant, Contestant.week_id == Week.id)
        .filter(Contestant.is_winner.is_(True))
        .order_by(Week.season_id, Week.week_number, Contestant.id)
        .all()
    )
    weeks = {}
    for week, winner in rows:
        entry = weeks.setdefault(week.id, {
            "week_id": week.id,
            "season_id": week.season_id,
            "week_number": week.week_number,
            "winners": [],
        })
        entry["winners"].append({"id": winner.id, "name": winner.name})
    return list(weeks.values())


def average_score():
    avg_result, count = db.session.query(func.avg(Score.value), func.count(Score.id)).one()
    return {
        "average": round(float(avg_result), 2) if avg_result is not None else None,
        "count": count,
    }


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


def most_successful_contestants():
    """Contestant(s) with the highest total points across all their episodes —
    a sum, not an average, so a strong run across many episodes isn't diluted
    the same way a single bad episode would drag down an average. Returns
    every contestant tied for the max, as a list, instead of arbitrarily
    picking one when there's a genuine tie."""
    rows = (
        db.session.query(
            Contestant.id, Contestant.name, func.sum(Score.value).label("total_score")
        )
        .join(Score, Score.contestant_id == Contestant.id)
        .group_by(Contestant.id, Contestant.name)
        .all()
    )
    if not rows:
        return []
    max_total = max(r.total_score for r in rows)
    return [
        {"contestant_id": r.id, "contestant_name": r.name, "total_score": int(r.total_score)}
        for r in rows
        if r.total_score == max_total
    ]


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
        "most_successful_contestants": most_successful_contestants(),
        "average_weekly_score": average_weekly_score(),
        "score_distribution": score_distribution(),
    }
