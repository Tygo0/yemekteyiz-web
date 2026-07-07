from datetime import date
from automation.parser.fusion import fuse
from automation.vision.mock_vision import MockVisionEngine


def test_fuse_builds_payload_from_vision_observations():
    vision = MockVisionEngine()
    observations = vision.analyze(["frame_0.jpg"], prompt="ignored")

    payload = fuse(
        week_id=42,
        video_url="https://youtube.com/watch?v=abc",
        broadcast_date=date(2026, 1, 5),
        vision_observations=observations,
    )

    assert payload.week_id == 42
    assert len(payload.contestants) == 4
    first = payload.contestants[0]
    assert first.name == "Ayşe"
    assert first.video_url == "https://youtube.com/watch?v=abc"
    assert first.broadcast_date == date(2026, 1, 5)
    assert len(first.dishes) == 1
    assert len(first.scores) == 3


def test_fuse_raises_on_no_observations():
    import pytest
    with pytest.raises(ValueError):
        fuse(week_id=1, video_url="x", broadcast_date=None, vision_observations=[])
