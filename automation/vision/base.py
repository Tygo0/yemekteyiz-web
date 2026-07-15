from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from automation.ocr.base import OcrResult
    from automation.speech.base import Transcript


@dataclass
class VisionObservation:
    frame_paths: list[str]
    structured: dict = field(default_factory=dict)


class VisionEngine(ABC):
    @abstractmethod
    def analyze(
        self,
        frame_paths: list[str],
        prompt: str,
        ocr_results: Optional[list["OcrResult"]] = None,
        transcript: Optional["Transcript"] = None,
    ) -> list[VisionObservation]:
        """
        Send frames (all at once — Gemini understands multi-image/video input
        natively) plus a prompt describing the expected JSON shape, and return
        the model's structured extraction (contestant names, dishes, scores).

        ocr_results/transcript are the already-computed outputs of this same
        pipeline run's OCR and speech stages. Gemini's implementation ignores
        them (it reads the raw frames directly), but a text-only local engine
        needs them as its actual evidence — the Pipeline always computes both
        stages anyway, so passing them through here avoids a second OCR/speech
        pass per engine.
        """
