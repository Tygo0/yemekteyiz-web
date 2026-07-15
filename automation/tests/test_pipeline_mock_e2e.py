from automation.pipeline import Pipeline
from automation.api_client.client import BackendClient
from automation.downloader.mock_downloader import MockDownloader
from automation.extractor.mock_extractor import MockExtractor
from automation.ocr.mock_ocr import MockOcrEngine
from automation.vision.mock_vision import MockVisionEngine
from automation.speech.mock_speech import MockSpeechEngine
from automation.validator.rules import ValidationError
from automation.parser.fusion import VisionRefusalError


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


def test_pipeline_accepts_non_four_contestant_count(live_backend):
    # Real weeks don't always have exactly 4 contestants (e.g. week 215 has
    # 5) -- a single valid contestant should import successfully, not be
    # rejected purely for an unusual count.
    vision = MockVisionEngine(contestants=[
        {"name": "Solo", "dishes": [{"name": "Soup", "category": "soup"}], "scores": [{"judge_name": "Zuhal", "value": 8}]}
    ])
    pipeline = _build_pipeline(live_backend, vision=vision)

    run = pipeline.run("https://youtube.com/watch?v=mock1", week_id=live_backend["week_id"])

    assert len(run.payload.contestants) == 1
    assert run.import_result["status"] == "imported"


def test_pipeline_rejects_empty_contestant_list(live_backend):
    vision = MockVisionEngine(contestants=[], is_cooking_competition=True)
    pipeline = _build_pipeline(live_backend, vision=vision)

    try:
        pipeline.run("https://youtube.com/watch?v=mock1", week_id=live_backend["week_id"])
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert any("at least 1 contestant" in e for e in exc.errors)


def test_pipeline_refuses_when_vision_reports_irrelevant_video(live_backend):
    vision = MockVisionEngine(is_cooking_competition=False)
    pipeline = _build_pipeline(live_backend, vision=vision)

    try:
        pipeline.run("https://youtube.com/watch?v=mock1", week_id=live_backend["week_id"])
        assert False, "expected VisionRefusalError"
    except VisionRefusalError as exc:
        assert "does not show a recognizable cooking competition" in str(exc)

    # The refusal happened locally (fuse() rejected before ever calling
    # /automation/import) — confirm it still shows up in Automation Logs,
    # not just as a local exception nobody but the CLI operator ever sees.
    import requests
    resp = requests.get(f"{live_backend['base_url']}/api/automation/logs", params={"week_id": live_backend["week_id"]})
    entries = resp.json()["logs"]
    assert any(e["status"] == "failure" and "cooking competition" in e["error_message"] for e in entries)
