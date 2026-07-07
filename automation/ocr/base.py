from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class OcrResult:
    frame_path: str
    text_lines: list[str] = field(default_factory=list)


class OcrEngine(ABC):
    @abstractmethod
    def read(self, frame_paths: list[str]) -> list[OcrResult]:
        """Run OCR over each frame, returning the raw text lines found."""
