from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Transcript:
    text: str
    segments: list[dict] = field(default_factory=list)  # {"start": float, "end": float, "text": str}


class SpeechEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, task: str = "translate") -> Transcript:
        """Transcribe the episode's audio track.

        task="translate" (default) has Whisper translate Turkish speech
        directly to English text, so any text-only vision engine downstream
        always has reliable English evidence to reason over — qwen2.5's
        instruction-following/reading of Turkish text is unreliable at the
        quantization used by LocalVisionEngine (see automation/vision/
        local_vision.py). Pass task="transcribe" to keep the original Turkish
        instead, e.g. for a debugging run.
        """
