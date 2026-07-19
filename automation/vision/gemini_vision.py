from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel
from automation.vision.base import VisionEngine, VisionObservation
from automation.ocr.base import OcrResult
from automation.progress import report
from automation.speech.base import Transcript


class _Dish(BaseModel):
    name: str
    category: str


class _Score(BaseModel):
    judge_name: str
    value: int


class _Contestant(BaseModel):
    name: str
    age: int | None = None
    profession: str | None = None
    city: str | None = None
    dishes: list[_Dish] = []
    scores: list[_Score] = []


class _WeekExtraction(BaseModel):
    # Forcing structured output with no "this doesn't apply" escape hatch
    # pushes the model toward fabricating a plausible-looking answer instead
    # of refusing, when the frames don't actually show a cooking competition.
    # Making the model commit to this judgment explicitly, separately from
    # the contestants list, gives it a truthful way out instead.
    is_cooking_competition: bool
    contestants: list[_Contestant]


class GeminiVisionEngine(VisionEngine):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def analyze(
        self,
        frame_paths: list[str],
        prompt: str,
        ocr_results: Optional[list[OcrResult]] = None,
        transcript: Optional[Transcript] = None,
    ) -> list[VisionObservation]:
        # ocr_results/transcript are unused here — Gemini reads the raw frames
        # directly and doesn't need pre-extracted text.
        report(f"  calling Gemini vision API with {len(frame_paths)} frame(s) (single request)...")
        # Sends every frame in one request — Gemini's multi-image understanding
        # lets it reconcile the same contestant/score appearing across frames
        # instead of us having to fuse per-frame guesses ourselves.
        parts = [types.Part.from_text(text=prompt)]
        for path in frame_paths:
            with open(path, "rb") as f:
                parts.append(types.Part.from_bytes(data=f.read(), mime_type="image/jpeg"))

        response = self._client.models.generate_content(
            model=self._model,
            contents=parts,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_WeekExtraction,
            ),
        )

        structured = (
            response.parsed.model_dump()
            if response.parsed
            else {"is_cooking_competition": False, "contestants": []}
        )
        return [VisionObservation(frame_paths=frame_paths, structured=structured)]
