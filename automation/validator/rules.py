"""
Enforces every rule from the automation blueprint before a payload is ever
POSTed to /api/automation/import — catching mistakes here gives a much
clearer error than letting the backend's own service-layer checks reject it.
"""
from typing import TYPE_CHECKING
from automation.models import WeekImportPayload

if TYPE_CHECKING:
    from automation.api_client.client import BackendClient

MIN_CONTESTANT_COUNT = 1


class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def validate(payload: WeekImportPayload, api_client: "BackendClient") -> None:
    errors: list[str] = []

    # Real weeks don't always have exactly 4 contestants (e.g. week 215 has
    # 5) -- only reject an empty extraction, not an unexpected count.
    if len(payload.contestants) < MIN_CONTESTANT_COUNT:
        errors.append(
            f"Expected at least {MIN_CONTESTANT_COUNT} contestant(s), got {len(payload.contestants)}"
        )

    names = [c.name.strip().lower() for c in payload.contestants if c.name and c.name.strip()]
    if len(names) != len(payload.contestants):
        errors.append("Every contestant must have a non-empty name")
    if len(set(names)) != len(names):
        errors.append("Duplicate contestant names within this import payload")

    for c in payload.contestants:
        if not c.dishes:
            errors.append(f"{c.name}: no dishes extracted")
        if not c.scores:
            errors.append(f"{c.name}: no scores extracted")
        for s in c.scores:
            if not (1 <= s.value <= 10):
                errors.append(f"{c.name}: score {s.value} out of range 1-10")
            if not s.judge_name or not s.judge_name.strip():
                errors.append(f"{c.name}: score missing judge name")

    week = api_client.get_week(payload.week_id)
    if week is None:
        errors.append(f"Week {payload.week_id} does not exist — an admin must create it first")
    else:
        existing_names = {c["name"].strip().lower() for c in api_client.list_contestants(payload.week_id)}
        duplicates = existing_names & set(names)
        if duplicates:
            errors.append(
                f"Contestant(s) already exist for week {payload.week_id}: {', '.join(sorted(duplicates))}"
            )

    if errors:
        raise ValidationError(errors)
