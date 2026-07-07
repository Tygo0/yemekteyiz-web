"""
One-off manual check that GEMINI_API_KEY actually works end-to-end: generates
a synthetic image with known text, sends it through the real
GeminiVisionEngine, and prints what comes back. Not a pytest test — run it
directly:

    python -m automation.scripts.verify_gemini
"""
import sys
import tempfile
import os
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from automation.config import get_settings
from automation.vision.gemini_vision import GeminiVisionEngine


def make_synthetic_frame(path: str) -> None:
    img = Image.new("RGB", (600, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "Contestant: Ayse", fill="black")
    draw.text((20, 60), "Dish: Mercimek Corbasi (soup)", fill="black")
    draw.text((20, 100), "Judge Zuhal: 8", fill="black")
    draw.text((20, 140), "Judge Somer: 9", fill="black")
    img.save(path)


def main() -> None:
    settings = get_settings()
    if not settings.gemini_api_key:
        print("GEMINI_API_KEY is not set in automation/.env — aborting.")
        return

    with tempfile.TemporaryDirectory() as tmp:
        frame_path = os.path.join(tmp, "frame_0.jpg")
        make_synthetic_frame(frame_path)

        engine = GeminiVisionEngine(api_key=settings.gemini_api_key)
        prompt = (
            "This image shows one contestant's card from a cooking competition. "
            "Extract the contestant's name, the dish they cooked (name + category), "
            "and every judge's score. Return JSON matching the given schema."
        )
        observations = engine.analyze([frame_path], prompt)

        print("Raw structured response:")
        print(observations[0].structured)


if __name__ == "__main__":
    main()
