from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExtractedMedia:
    frame_paths: list[str]
    audio_path: str


class Extractor(ABC):
    @abstractmethod
    def extract(self, video_path: str, dest_dir: str) -> ExtractedMedia:
        """Split a video into frames (for OCR/vision) and an audio track (for speech)."""
