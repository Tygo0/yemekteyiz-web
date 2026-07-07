"""
Real (non-mock) check that GEMINI_API_KEY actually authenticates and that
GeminiVisionEngine's structured-output parsing matches what Gemini returns.
Skipped by default so the rest of the suite stays network-free; run on demand
with `pytest automation/tests/test_gemini_smoke.py -v` whenever you want to
reconfirm the key/model still works (e.g. after a model rename or key rotation).
"""
import os
import pytest
from automation.config import get_settings

pytestmark = pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"), reason="requires a real GEMINI_API_KEY"
)


def test_gemini_vision_reads_synthetic_frame(tmp_path):
    from PIL import Image, ImageDraw
    from automation.vision.gemini_vision import GeminiVisionEngine

    frame_path = tmp_path / "frame_0.jpg"
    img = Image.new("RGB", (600, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "Contestant: Ayse", fill="black")
    draw.text((20, 60), "Dish: Mercimek Corbasi (soup)", fill="black")
    draw.text((20, 100), "Judge Zuhal: 8", fill="black")
    img.save(frame_path)

    settings = get_settings()
    engine = GeminiVisionEngine(api_key=settings.gemini_api_key)
    observations = engine.analyze(
        [str(frame_path)],
        "Extract the contestant's name, dish (name + category), and judge scores as JSON.",
    )

    contestants = observations[0].structured.get("contestants", [])
    assert contestants, "Gemini returned no contestants for a clearly-labeled synthetic frame"
    assert contestants[0]["name"].lower().startswith("ayse")
    assert any(s["value"] == 8 for s in contestants[0]["scores"])
