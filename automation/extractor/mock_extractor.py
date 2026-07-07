import os
from automation.extractor.base import Extractor, ExtractedMedia


class MockExtractor(Extractor):
    """Fakes ffmpeg: writes empty placeholder frame/audio files so downstream
    stages have real paths without needing a real video or ffmpeg installed."""

    def __init__(self, frame_count: int = 4):
        self._frame_count = frame_count

    def extract(self, video_path: str, dest_dir: str) -> ExtractedMedia:
        os.makedirs(dest_dir, exist_ok=True)
        frame_paths = []
        for i in range(self._frame_count):
            frame_path = os.path.join(dest_dir, f"frame_{i}.jpg")
            with open(frame_path, "wb"):
                pass
            frame_paths.append(frame_path)

        audio_path = os.path.join(dest_dir, "audio.wav")
        with open(audio_path, "wb"):
            pass

        return ExtractedMedia(frame_paths=frame_paths, audio_path=audio_path)
