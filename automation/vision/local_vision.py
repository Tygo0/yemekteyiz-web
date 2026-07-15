"""
Local, API-free replacement for GeminiVisionEngine: a small local Ollama model
(e.g. qwen2.5:7b-instruct) reads the episode's OCR text and English transcript
and produces the same structured extraction shape Gemini does.

qwen2.5:7b-instruct-q4_K_M is unreliable at genuinely reading/writing Turkish —
video-understanding's own testing found it drifting into the wrong language
entirely, and producing real mistranslation errors even when the task was
just "translate this". To avoid that failure mode here, the model is never
asked to generate Turkish text:

  - The transcript it reads is Whisper's English translation, not the Turkish
    original (Whisper does that translation, not the LLM).
  - Every Turkish proper noun (contestant name, city, profession, dish name,
    judge name) is resolved by having the model pick an *index* into a
    numbered list of raw OCR fragments, rather than typing the text itself.
    A plain Python lookup then substitutes the literal OCR string back in, so
    the Turkish text reaching the database is always a byte-exact OCR copy,
    never something the model generated.

The one place this doesn't fully eliminate cross-lingual reading is dish
category classification (e.g. deciding "Mercimek Corbasi" -> "soup"), which
still requires the model to read a short OCR fragment. That's a much smaller,
better-scoped task than open-ended translation/summarization, but it isn't
zero-risk, and it's worth keeping an eye on once this runs against real
footage.
"""
from typing import Literal, Optional

import ollama
from pydantic import BaseModel

from automation.ocr.base import OcrResult
from automation.speech.base import Transcript
from automation.vision.base import VisionEngine, VisionObservation
from automation.vision.persistent_fragment_filter import filter_persistent_fragments

DishCategory = Literal["soup", "appetizer", "main_course", "dessert", "beverage"]

DEFAULT_MODEL = "qwen2.5:7b-instruct-q4_K_M"

# No index means "not found among the OCR fragments" — kept out of Literal/int
# range so the model has an explicit way to say so instead of guessing 0.
NO_INDEX = -1

EXTRACTION_PROMPT = """You are extracting structured data about a Turkish cooking \
competition episode from two pieces of evidence. Do not translate, retype, or \
paraphrase any Turkish text anywhere in your answer — whenever a field needs \
Turkish text (a person's name, a city, a profession, a dish name), answer with \
the *index number* of the matching item in the OCR fragment list below, not the \
text itself. Use {no_index} for any index you cannot find.

=== English transcript (translated from Turkish) ===
{transcript}

=== OCR text fragments detected on screen (Turkish, numbered) ===
{ocr_fragments}

First decide honestly whether the evidence actually shows a Turkish cooking \
competition episode (contestants cooking dishes, judges scoring them). If you \
are not confident, or the evidence doesn't support it, set is_cooking_competition \
to false and return an empty contestants list — do not invent plausible-sounding \
contestants, dishes, or scores that aren't clearly supported by the evidence.

If it does: identify each contestant. For each, give the OCR fragment index for \
their name (required), age as a plain number if known (or null), and OCR \
fragment indices for profession and city if known (or {no_index}). List their \
dishes: each dish's OCR fragment index for its name, plus a category classified \
into exactly one of soup / appetizer / main_course / dessert / beverage. List \
their scores: each score's OCR fragment index for the judge's name, plus the \
integer value (1-10) shown on screen.
"""


class _IndexedDish(BaseModel):
    name_index: int
    category: DishCategory


class _IndexedScore(BaseModel):
    judge_name_index: int
    value: int


class _IndexedContestant(BaseModel):
    name_index: int
    age: Optional[int] = None
    profession_index: int = NO_INDEX
    city_index: int = NO_INDEX
    dishes: list[_IndexedDish] = []
    scores: list[_IndexedScore] = []


class _IndexedExtraction(BaseModel):
    is_cooking_competition: bool
    contestants: list[_IndexedContestant] = []


def _collect_ocr_fragments(ocr_results: Optional[list[OcrResult]]) -> list[str]:
    """Flatten every frame's OCR lines into one deduplicated, order-preserving
    list — the numbered candidate list the model picks indices from."""
    if not ocr_results:
        return []
    seen: dict[str, None] = {}
    for result in ocr_results:
        for line in result.text_lines:
            line = line.strip()
            if line and line not in seen:
                seen[line] = None
    return list(seen.keys())


def _resolve(fragments: list[str], index: Optional[int]) -> Optional[str]:
    """Look up a model-chosen index in the literal OCR fragment list. Returns
    None for a missing/out-of-range index rather than raising, so a partial
    extraction still reaches the validator (which will reject it with a clear
    reason) instead of crashing the pipeline on a bad index."""
    if index is None or index == NO_INDEX or not (0 <= index < len(fragments)):
        return None
    return fragments[index]


def _build_prompt(transcript_text: str, fragments: list[str]) -> str:
    numbered = "\n".join(f"[{i}] {frag}" for i, frag in enumerate(fragments)) or "(none detected)"
    return EXTRACTION_PROMPT.format(
        transcript=transcript_text or "(no speech detected)",
        ocr_fragments=numbered,
        no_index=NO_INDEX,
    )


def _resolve_extraction(extraction: _IndexedExtraction, fragments: list[str]) -> dict:
    """Turn the model's index-only output into the same structured dict shape
    GeminiVisionEngine.analyze() returns, by substituting literal OCR text
    back in for every index — this is the step that guarantees Turkish text
    in the final payload is always a verbatim OCR copy, never model output."""
    if not extraction.is_cooking_competition:
        return {"is_cooking_competition": False, "contestants": []}

    contestants = []
    for c in extraction.contestants:
        name = _resolve(fragments, c.name_index)
        contestants.append({
            "name": name if name is not None else "",
            "age": c.age,
            "profession": _resolve(fragments, c.profession_index),
            "city": _resolve(fragments, c.city_index),
            "dishes": [
                {"name": _resolve(fragments, d.name_index) or "", "category": d.category}
                for d in c.dishes
            ],
            "scores": [
                {"judge_name": _resolve(fragments, s.judge_name_index) or "", "value": s.value}
                for s in c.scores
            ],
        })
    return {"is_cooking_competition": True, "contestants": contestants}


class LocalVisionEngine(VisionEngine):
    """Drop-in VisionEngine backed by a local Ollama model instead of Gemini.
    Ignores frame_paths/prompt (the arguments GeminiVisionEngine uses) in
    favor of ocr_results/transcript, which is where its actual evidence
    comes from — see module docstring for why."""

    def __init__(self, model: str = DEFAULT_MODEL, host: Optional[str] = None):
        self._model = model
        self._client = ollama.Client(host=host) if host else ollama.Client()

    def analyze(
        self,
        frame_paths: list[str],
        prompt: str,
        ocr_results: Optional[list[OcrResult]] = None,
        transcript: Optional[Transcript] = None,
    ) -> list[VisionObservation]:
        # Strip persistent watermark/logo noise before the model ever sees
        # it — see persistent_fragment_filter's module docstring for why this
        # matters on real footage (351 "contestants" instead of 4, mostly
        # OCR misreads of the show's own on-screen watermark).
        filtered_ocr_results = filter_persistent_fragments(ocr_results) if ocr_results else ocr_results
        fragments = _collect_ocr_fragments(filtered_ocr_results)
        transcript_text = transcript.text if transcript else ""

        response = self._client.generate(
            model=self._model,
            prompt=_build_prompt(transcript_text, fragments),
            format=_IndexedExtraction.model_json_schema(),
        )

        try:
            extraction = _IndexedExtraction.model_validate_json(response["response"])
        except (KeyError, ValueError):
            structured = {"is_cooking_competition": False, "contestants": []}
        else:
            structured = _resolve_extraction(extraction, fragments)

        return [VisionObservation(frame_paths=frame_paths, structured=structured)]
