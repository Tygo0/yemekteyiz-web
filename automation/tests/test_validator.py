import pytest
from automation.models import WeekImportPayload, ContestantData, DishData, ScoreData
from automation.validator.rules import validate, ValidationError


class _FakeApiClient:
    def __init__(self, week_exists=True, existing_names=None):
        self._week_exists = week_exists
        self._existing_names = existing_names or []

    def get_week(self, week_id):
        return {"id": week_id} if self._week_exists else None

    def list_contestants(self, week_id):
        return [{"name": n} for n in self._existing_names]


def _valid_contestant(name):
    return ContestantData(
        name=name,
        dishes=[DishData(name="Soup", category="soup")],
        scores=[ScoreData(judge_name="Zuhal", value=8)],
    )


def test_valid_payload_passes():
    payload = WeekImportPayload(week_id=1, contestants=[_valid_contestant(n) for n in "ABCD"])
    validate(payload, _FakeApiClient())  # should not raise


def test_non_four_contestant_count_is_accepted():
    # Real weeks don't always have exactly 4 (e.g. week 215 has 5) -- as long
    # as every contestant is otherwise valid, an unusual count isn't an error.
    payload = WeekImportPayload(week_id=1, contestants=[_valid_contestant(n) for n in "ABCDE"])
    validate(payload, _FakeApiClient())  # should not raise


def test_empty_contestant_list_rejected():
    payload = WeekImportPayload(week_id=1, contestants=[])
    with pytest.raises(ValidationError) as exc:
        validate(payload, _FakeApiClient())
    assert any("at least 1 contestant" in e for e in exc.value.errors)


def test_duplicate_names_in_payload_rejected():
    payload = WeekImportPayload(week_id=1, contestants=[_valid_contestant("A")] * 4)
    with pytest.raises(ValidationError):
        validate(payload, _FakeApiClient())


def test_missing_week_rejected():
    payload = WeekImportPayload(week_id=1, contestants=[_valid_contestant(n) for n in "ABCD"])
    with pytest.raises(ValidationError) as exc:
        validate(payload, _FakeApiClient(week_exists=False))
    assert any("does not exist" in e for e in exc.value.errors)


def test_contestant_already_in_week_rejected():
    payload = WeekImportPayload(week_id=1, contestants=[_valid_contestant(n) for n in "ABCD"])
    with pytest.raises(ValidationError) as exc:
        validate(payload, _FakeApiClient(existing_names=["a"]))
    assert any("already exist" in e for e in exc.value.errors)


def test_score_out_of_range_rejected():
    contestant = _valid_contestant("A")
    contestant.scores = [ScoreData(judge_name="Zuhal", value=99)]
    payload = WeekImportPayload(week_id=1, contestants=[contestant, *[_valid_contestant(n) for n in "BCD"]])
    with pytest.raises(ValidationError) as exc:
        validate(payload, _FakeApiClient())
    assert any("out of range" in e for e in exc.value.errors)


def test_no_dishes_rejected():
    contestant = _valid_contestant("A")
    contestant.dishes = []
    payload = WeekImportPayload(week_id=1, contestants=[contestant, *[_valid_contestant(n) for n in "BCD"]])
    with pytest.raises(ValidationError) as exc:
        validate(payload, _FakeApiClient())
    assert any("no dishes" in e for e in exc.value.errors)
