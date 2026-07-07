import os
import subprocess
from automation.extractor.base import Extractor, ExtractedMedia


class FfmpegExtractor(Extractor):
    """Requires the `ffmpeg` binary on PATH."""

    def __init__(self, frame_interval_seconds: int = 30):
        self._frame_interval_seconds = frame_interval_seconds

    def extract(self, video_path: str, dest_dir: str) -> ExtractedMedia:
        os.makedirs(dest_dir, exist_ok=True)

        frame_pattern = os.path.join(dest_dir, "frame_%04d.jpg")
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", video_path,
                "-vf", f"fps=1/{self._frame_interval_seconds}",
                frame_pattern,
            ],
            check=True, capture_output=True,
        )
        frame_paths = sorted(
            os.path.join(dest_dir, name) for name in os.listdir(dest_dir) if name.startswith("frame_")
        )

        audio_path = os.path.join(dest_dir, "audio.wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path],
            check=True, capture_output=True,
        )

        return ExtractedMedia(frame_paths=frame_paths, audio_path=audio_path)
