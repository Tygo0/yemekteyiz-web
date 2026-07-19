"""
Manual entrypoint for running the pipeline once against a single video.

Mock run (no external services needed):
    python -m automation.cli --video-url https://youtube.com/watch?v=x --week-id 1 --mock

Real run (requires GEMINI_API_KEY etc. in automation/.env):
    python -m automation.cli --video-url https://youtube.com/watch?v=x --week-id 1
"""
import argparse
from automation.config import get_settings
from automation.pipeline import Pipeline
from automation.api_client.client import BackendClient


def build_pipeline(mock: bool) -> Pipeline:
    settings = get_settings()
    api_client = BackendClient(settings.backend_url, settings.admin_username, settings.admin_password)

    if mock:
        from automation.downloader.mock_downloader import MockDownloader
        from automation.extractor.mock_extractor import MockExtractor
        from automation.ocr.mock_ocr import MockOcrEngine
        from automation.vision.mock_vision import MockVisionEngine
        from automation.speech.mock_speech import MockSpeechEngine

        return Pipeline(
            downloader=MockDownloader(),
            extractor=MockExtractor(),
            ocr=MockOcrEngine(),
            vision=MockVisionEngine(),
            speech=MockSpeechEngine(),
            api_client=api_client,
        )

    from automation.downloader.ytdlp_downloader import YtDlpDownloader
    from automation.extractor.ffmpeg_extractor import FfmpegExtractor
    from automation.ocr.easyocr_engine import EasyOcrEngine
    from automation.speech.whisper_engine import WhisperSpeechEngine

    if settings.vision_engine == "local":
        from automation.vision.local_vision import LocalVisionEngine

        vision = LocalVisionEngine(model=settings.ollama_model, host=settings.ollama_host or None)
    elif settings.vision_engine == "gemini":
        from automation.vision.gemini_vision import GeminiVisionEngine

        vision = GeminiVisionEngine(api_key=settings.gemini_api_key)
    else:
        raise ValueError(
            f"Unknown AUTOMATION_VISION_ENGINE={settings.vision_engine!r}, expected 'gemini' or 'local'"
        )

    return Pipeline(
        downloader=YtDlpDownloader(),
        extractor=FfmpegExtractor(),
        ocr=EasyOcrEngine(),
        vision=vision,
        speech=WhisperSpeechEngine(),
        api_client=api_client,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-url", required=True)
    parser.add_argument("--week-id", required=True, type=int)
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    pipeline = build_pipeline(mock=args.mock)
    run = pipeline.run(args.video_url, args.week_id)
    print(run.import_result)


if __name__ == "__main__":
    main()
