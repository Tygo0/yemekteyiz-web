from automation.pipeline import Pipeline
from automation.api_client.client import BackendClient
from automation.downloader.mock_downloader import MockDownloader
from automation.extractor.mock_extractor import MockExtractor
from automation.ocr.mock_ocr import MockOcrEngine
from automation.vision.mock_vision import MockVisionEngine
from automation.speech.mock_speech import MockSpeechEngine
from automation.validator.rules import ValidationError


def _build_pipeline(live_backend, vision=None):
    api_client = BackendClient(
        live_backend["base_url"], live_backend["username"], live_backend["password"]
    )
    return Pipeline(
        downloader=MockDownloader(),
        extractor=MockExtractor(),
        ocr=MockOcrEngine(),
        vision=vision or MockVisionEngine(),
        speech=MockSpeechEngine(),
        api_client=api_client,
    )


def test_full_mock_pipeline_imports_into_real_backend(live_backend):
    pipeline = _build_pipeline(live_backend)

    run = pipeline.run("https://youtube.com/watch?v=mock1", week_id=live_backend["week_id"])

    assert len(run.payload.contestants) == 4
    assert run.import_result["status"] == "imported"
    assert len(run.import_result["contestants"]) == 4
    assert run.ocr_text_lines
    assert run.speech_transcript


def test_pipeline_rejects_when_week_missing(live_backend):
    pipeline = _build_pipeline(live_backend)
    try:
        pipeline.run("https://youtube.com/watch?v=mock1", week_id=999999)
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert any("does not exist" in e for e in exc.errors)


def test_pipeline_rejects_wrong_contestant_count(live_backend):
    vision = MockVisionEngine(contestants=[
        {"name": "Solo", "dishes": [{"name": "Soup", "category": "soup"}], "scores": [{"judge_name": "Zuhal", "value": 8}]}
    ])
    pipeline = _build_pipeline(live_backend, vision=vision)

    try:
        pipeline.run("https://youtube.com/watch?v=mock1", week_id=live_backend["week_id"])
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert any("Expected exactly 4 contestants" in e for e in exc.errors)
