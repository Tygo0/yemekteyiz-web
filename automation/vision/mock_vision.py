from automation.vision.base import VisionEngine, VisionObservation


class MockVisionEngine(VisionEngine):
    """Fakes the Gemini vision call with a synthetic aggregated JSON extraction
    covering a full week (4 contestants), so parser/validator can be exercised
    without spending real API credits."""

    def __init__(self, contestants: list[dict] | None = None):
        self._contestants = contestants if contestants is not None else _default_contestants()

    def analyze(self, frame_paths: list[str], prompt: str) -> list[VisionObservation]:
        return [VisionObservation(frame_paths=frame_paths, structured={"contestants": self._contestants})]


def _default_contestants() -> list[dict]:
    return [
        {
            "name": name,
            "age": 30,
            "profession": "Chef",
            "city": "Istanbul",
            "dishes": [{"name": "Mercimek Çorbası", "category": "soup"}],
            "scores": [
                {"judge_name": "Zuhal", "value": 8},
                {"judge_name": "Somer", "value": 9},
                {"judge_name": "Danilo", "value": 7},
            ],
        }
        for name in ("Ayşe", "Mehmet", "Fatma", "Ali")
    ]
