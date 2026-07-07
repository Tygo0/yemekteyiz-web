"""
Orchestrates the full Discovery -> Download -> Media Extraction -> Visual
Understanding -> Speech Understanding -> Data Fusion -> Validation -> Backend
Integration pipeline described in docs/ARCHITECTURE.md. Every stage is
injected, so the same Pipeline class runs identically whether it's wired to
all-mock stages (tests) or real ones (production).
"""
import os
import tempfile
from dataclasses import dataclass
from datetime import date

from automation.downloader.base import Downloader
from automation.extractor.base import Extractor
from automation.ocr.base import OcrEngine
from automation.vision.base import VisionEngine
from automation.speech.base import SpeechEngine
from automation.api_client.client import BackendClient
from automation.parser.fusion import fuse
from automation.validator.rules import validate
from automation.models import WeekImportPayload

VISION_PROMPT = (
    "You are watching frames from a Turkish cooking competition episode. "
    "Identify exactly four contestants. For each, extract their name, age, "
    "profession, city (if shown), the dishes they cooked (name + one of "
    "soup/appetizer/main_course/dessert/beverage), and every judge's score "
    "(judge name + integer 1-10) shown on screen. Return structured JSON only."
)


@dataclass
class PipelineRun:
    payload: WeekImportPayload
    ocr_text_lines: list[str]
    speech_transcript: str
    import_result: dict


class Pipeline:
    def __init__(
        self,
        downloader: Downloader,
        extractor: Extractor,
        ocr: OcrEngine,
        vision: VisionEngine,
        speech: SpeechEngine,
        api_client: BackendClient,
    ):
        self.downloader = downloader
        self.extractor = extractor
        self.ocr = ocr
        self.vision = vision
        self.speech = speech
        self.api_client = api_client

    def run(self, video_url: str, week_id: int, broadcast_date: date | None = None, work_dir: str | None = None) -> PipelineRun:
        work_dir = work_dir or tempfile.mkdtemp(prefix="automation_")
        os.makedirs(work_dir, exist_ok=True)

        video = self.downloader.download(video_url, work_dir)
        media = self.extractor.extract(video.video_path, work_dir)

        ocr_results = self.ocr.read(media.frame_paths)
        vision_observations = self.vision.analyze(media.frame_paths, VISION_PROMPT)
        transcript = self.speech.transcribe(media.audio_path)

        payload = fuse(
            week_id=week_id,
            video_url=video_url,
            broadcast_date=broadcast_date,
            vision_observations=vision_observations,
        )

        validate(payload, self.api_client)

        result = self.api_client.import_week(payload)

        ocr_lines = [line for r in ocr_results for line in r.text_lines]
        return PipelineRun(
            payload=payload,
            ocr_text_lines=ocr_lines,
            speech_transcript=transcript.text,
            import_result=result,
        )
