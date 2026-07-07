from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VisionObservation:
    frame_paths: list[str]
    structured: dict = field(default_factory=dict)


class VisionEngine(ABC):
    @abstractmethod
    def analyze(self, frame_paths: list[str], prompt: str) -> list[VisionObservation]:
        """
        Send frames (all at once — Gemini understands multi-image/video input
        natively) plus a prompt describing the expected JSON shape, and return
        the model's structured extraction (contestant names, dishes, scores).
        """
