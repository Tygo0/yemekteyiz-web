from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Transcript:
    text: str
    segments: list[dict] = field(default_factory=list)  # {"start": float, "end": float, "text": str}


class SpeechEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> Transcript:
        """Transcribe the episode's audio track."""
