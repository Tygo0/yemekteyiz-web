from app.extensions import db
from app.models import AutomationImportLog, AutomationImportStatus
from app.services import week_service, contestant_service, episode_service, dish_service, score_service
from app.utils.errors import ConflictError


def import_week(data):
    # "Week must already exist" — automation never creates weeks itself, only
    # populates one an admin already created (manual system before automation).
    week = week_service.get_week(data["week_id"])

    existing_names = {c.name.strip().lower() for c in contestant_service.list_contestants(week_id=week.id)}

    incoming_names = [c["name"].strip().lower() for c in data["contestants"]]
    if len(set(incoming_names)) != len(incoming_names):
        raise ConflictError("Duplicate contestant name within the same import payload")
    duplicates = existing_names & set(incoming_names)
    if duplicates:
        raise ConflictError(f"Contestant(s) already exist for this week: {', '.join(sorted(duplicates))}")

    created = []
    for contestant_data in data["contestants"]:
        contestant = contestant_service.create_contestant({
            "week_id": week.id,
            "name": contestant_data["name"],
            "age": contestant_data.get("age"),
            "profession": contestant_data.get("profession"),
            "city": contestant_data.get("city"),
            "biography": contestant_data.get("biography"),
            "photo_url": contestant_data.get("photo_url"),
        })

        episode = episode_service.create_episode({
            "contestant_id": contestant.id,
            "broadcast_date": contestant_data.get("broadcast_date"),
            "video_url": contestant_data.get("video_url"),
        })

        dishes = [
            dish_service.create_dish({
                "episode_id": episode.id,
                "name": dish_data["name"],
                "category": dish_data["category"],
            })
            for dish_data in contestant_data.get("dishes", [])
        ]

        scores = [
            score_service.create_score({
                "episode_id": episode.id,
                "contestant_id": contestant.id,
                "judge_name": score_data["judge_name"],
                "value": score_data["value"],
            })
            for score_data in contestant_data.get("scores", [])
        ]

        created.append({
            "contestant": contestant,
            "episode": episode,
            "dishes": dishes,
            "scores": scores,
        })

    return created


def log_import(week_id, success, contestant_count=0, error_message=None):
    log = AutomationImportLog(
        week_id=week_id,
        status=AutomationImportStatus.SUCCESS if success else AutomationImportStatus.FAILURE,
        contestant_count=contestant_count,
        error_message=error_message,
    )
    db.session.add(log)
    db.session.commit()
    return log


def list_import_logs(week_id=None):
    query = AutomationImportLog.query
    if week_id is not None:
        query = query.filter_by(week_id=week_id)
    return query.order_by(AutomationImportLog.created_at.desc()).all()
