"""
Real (non-mock) check that a local Ollama server + model can actually perform
the indexed extraction LocalVisionEngine relies on. Skipped by default so the
rest of the suite stays network/GPU-free; run on demand once Ollama is up:

    ollama pull qwen2.5:7b-instruct-q4_K_M
    ollama serve
    pytest automation/tests/test_local_vision_smoke.py -v

This doesn't assert extraction *accuracy* (a 7B local model on synthetic
evidence isn't a meaningful accuracy bar) — it asserts the one invariant the
whole design depends on: any name/city/dish/judge text that comes back is
either empty or a byte-exact copy of one of the OCR fragments it was given,
never text the model generated itself.
"""
import pytest
from automation.config import get_settings


def _ollama_reachable() -> bool:
    try:
        import ollama

        ollama.Client(host=get_settings().ollama_host or None).list()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _ollama_reachable(), reason="requires a running local Ollama server")


def test_local_vision_only_returns_literal_ocr_text():
    from automation.ocr.base import OcrResult
    from automation.speech.base import Transcript
    from automation.vision.local_vision import LocalVisionEngine

    settings = get_settings()
    engine = LocalVisionEngine(model=settings.ollama_model, host=settings.ollama_host or None)

    fragments = ["Ayse", "Istanbul", "Mercimek Corbasi", "Zuhal", "8"]
    ocr_results = [OcrResult(frame_path="frame_0.jpg", text_lines=fragments)]
    transcript = Transcript(
        text="One contestant named Ayse from Istanbul cooked a lentil soup. Judge Zuhal scored it 8.",
        segments=[],
    )

    observations = engine.analyze([], "", ocr_results=ocr_results, transcript=transcript)
    structured = observations[0].structured

    assert isinstance(structured["is_cooking_competition"], bool)
    for contestant in structured["contestants"]:
        for field in ("name", "profession", "city"):
            value = contestant.get(field)
            assert value == "" or value is None or value in fragments, (
                f"{field}={value!r} is not empty and not a literal OCR fragment — "
                "the model generated text instead of picking an index"
            )
        for dish in contestant["dishes"]:
            assert dish["name"] == "" or dish["name"] in fragments
            assert dish["category"] in (
                "soup", "appetizer", "main_course", "dessert", "beverage"
            )
        for score in contestant["scores"]:
            assert score["judge_name"] == "" or score["judge_name"] in fragments
            assert isinstance(score["value"], int)
