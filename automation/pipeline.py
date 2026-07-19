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
from automation.progress import report

TOTAL_STAGES = 7

VISION_PROMPT = (
    "These frames may or may not be from a Turkish cooking competition episode "
    "(contestants cooking dishes, judges scoring them on screen). First decide "
    "honestly whether that's actually what's shown — set is_cooking_competition "
    "to false and return an empty contestants list if it isn't, or if you are not "
    "confident. Do not invent or guess plausible-sounding contestants, dishes, or "
    "scores that are not clearly visible in the frames. Only if it clearly is a "
    "cooking competition: set is_cooking_competition to true and identify exactly "
    "four contestants, extracting for each their name, age, profession, city (if "
    "shown), the dishes they cooked (name + one of soup/appetizer/main_course/"
    "dessert/beverage), and every judge's score (judge name + integer 1-10) shown "
    "on screen. Return structured JSON only."
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

        report(f"[1/{TOTAL_STAGES}] Downloading {video_url}...")
        video = self.downloader.download(video_url, work_dir)

        report(f"[2/{TOTAL_STAGES}] Extracting frames + audio...")
        media = self.extractor.extract(video.video_path, work_dir)
        report(f"  extracted {len(media.frame_paths)} frame(s)")

        report(f"[3/{TOTAL_STAGES}] Running OCR on {len(media.frame_paths)} frame(s)...")
        ocr_results = self.ocr.read(media.frame_paths)

        report(f"[4/{TOTAL_STAGES}] Transcribing audio...")
        transcript = self.speech.transcribe(media.audio_path)

        report(f"[5/{TOTAL_STAGES}] Analyzing vision ({type(self.vision).__name__})...")
        # ocr_results/transcript are computed once here and handed to whichever
        # vision engine is wired in — GeminiVisionEngine ignores them (it reads
        # the raw frames directly), LocalVisionEngine relies on them as its
        # actual evidence. Avoids a second OCR/speech pass per engine.
        vision_observations = self.vision.analyze(
            media.frame_paths, VISION_PROMPT, ocr_results=ocr_results, transcript=transcript
        )

        report(f"[6/{TOTAL_STAGES}] Fusing + validating extraction...")
        try:
            payload = fuse(
                week_id=week_id,
                video_url=video_url,
                broadcast_date=broadcast_date,
                vision_observations=vision_observations,
            )
            validate(payload, self.api_client)
        except Exception as e:
            # fuse()/validate() reject locally, before ever reaching
            # /automation/import — without reporting it explicitly here,
            # this failure would be invisible in GET /automation/logs.
            self.api_client.report_failure(week_id, str(e))
            raise

        report(f"[7/{TOTAL_STAGES}] Importing {len(payload.contestants)} contestant(s) to backend...")
        result = self.api_client.import_week(payload)
        report("Done.")

        ocr_lines = [line for r in ocr_results for line in r.text_lines]
        return PipelineRun(
            payload=payload,
            ocr_text_lines=ocr_lines,
            speech_transcript=transcript.text,
            import_result=result,
        )
