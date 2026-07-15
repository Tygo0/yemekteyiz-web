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

A first version handed the model one flat, deduplicated fragment list for
the *whole* episode at once. Against a real ~90-minute episode that produced
351 "contestants" instead of 4 — mostly OCR misreads of the show's own
on-screen watermark, and the model unable to cluster hundreds of unrelated
fragments into ~4 people. This version instead:

  1. Filters out persistent watermark/logo noise first (persistent_
     fragment_filter), since a genuine contestant/dish/score graphic is only
     on screen briefly, unlike a watermark.
  2. Clusters the remaining frames by temporal/content proximity
     (frame_clustering), so consecutive frames showing the same on-screen
     graphic become one small extraction unit instead of hundreds of loose
     fragments.
  3. Runs one extraction call per cluster, asking only "is this graphic
     relevant, and if so what does it show" — bounded to that cluster's own
     small fragment list, not the whole episode's.
  4. Fuses the per-cluster partial extractions (cluster_fusion) into the
     final contestants list, attributing dish/score-only clusters (no name of
     their own) to whichever contestant was most recently established, and
     merging re-mentions of an already-seen name (OCR renders it slightly
     differently card to card) into the same record instead of duplicating.

The one place this doesn't fully eliminate cross-lingual reading is dish
category classification (e.g. deciding "Mercimek Corbasi" -> "soup"), which
still requires the model to read a short OCR fragment. That's a much smaller,
better-scoped task than open-ended translation/summarization, but it isn't
zero-risk.
"""
from typing import Literal, Optional

import ollama
from pydantic import BaseModel

from automation.ocr.base import OcrResult
from automation.speech.base import Transcript
from automation.vision.base import VisionEngine, VisionObservation
from automation.vision.cluster_fusion import fuse_cluster_extractions
from automation.vision.frame_clustering import FrameCluster, cluster_by_proximity
from automation.vision.persistent_fragment_filter import filter_persistent_fragments

DishCategory = Literal["soup", "appetizer", "main_course", "dessert", "beverage"]

DEFAULT_MODEL = "qwen2.5:7b-instruct-q4_K_M"

# No index means "not found among the OCR fragments" — kept out of Literal/int
# range so the model has an explicit way to say so instead of guessing 0.
NO_INDEX = -1

CLUSTER_PROMPT = """You are looking at one on-screen graphic from a Turkish cooking \
competition episode — a small set of OCR text fragments detected together on the same \
overlay (for example: a contestant's name card, a dish name overlay, or a judge's score \
reveal). Do not translate, retype, or paraphrase any Turkish text in your answer — \
whenever a field needs Turkish text, answer with the *index number* of the matching \
fragment below, not the text itself. Use {no_index} for any index you cannot find.

=== English transcript for context (translated from Turkish) ===
{transcript}

=== OCR text fragments from this one on-screen graphic (Turkish, numbered) ===
{ocr_fragments}

First decide honestly whether this graphic actually shows contestant/dish/score \
information relevant to the competition — not, for example, an unrelated caption, \
narration subtitle, or something you can't make sense of. If not, set is_relevant to \
false and leave every other field at its default.

If it does, fill in whichever fields *this specific graphic* actually shows, and leave \
the rest at their default — most graphics only show one or two things, not everything \
at once: the OCR fragment index for a contestant's name if shown, their age as a plain \
number if shown, OCR fragment indices for profession and city if shown, any dish shown \
(OCR fragment index for its name, plus a category classified into exactly one of \
soup / appetizer / main_course / dessert / beverage), and any judge's score shown (OCR \
fragment index for the judge's name, plus the integer value 1-10).
"""


class _ClusterDish(BaseModel):
    name_index: int
    category: DishCategory


class _ClusterScore(BaseModel):
    judge_name_index: int
    value: int


class _ClusterExtraction(BaseModel):
    is_relevant: bool
    name_index: int = NO_INDEX
    age: Optional[int] = None
    profession_index: int = NO_INDEX
    city_index: int = NO_INDEX
    dishes: list[_ClusterDish] = []
    scores: list[_ClusterScore] = []


def _resolve(fragments: list[str], index: Optional[int]) -> Optional[str]:
    """Look up a model-chosen index in the literal OCR fragment list. Returns
    None for a missing/out-of-range index rather than raising, so a partial
    extraction still reaches the validator (which will reject it with a clear
    reason) instead of crashing the pipeline on a bad index."""
    if index is None or index == NO_INDEX or not (0 <= index < len(fragments)):
        return None
    return fragments[index]


def _build_cluster_prompt(transcript_text: str, fragments: list[str]) -> str:
    numbered = "\n".join(f"[{i}] {frag}" for i, frag in enumerate(fragments)) or "(none detected)"
    return CLUSTER_PROMPT.format(
        transcript=transcript_text or "(no speech detected)",
        ocr_fragments=numbered,
        no_index=NO_INDEX,
    )


def _resolve_cluster_extraction(extraction: _ClusterExtraction, fragments: list[str]) -> Optional[dict]:
    """Turn one cluster's index-only model output into a partial contestant
    dict (any field may be None/empty — most graphics only show one or two
    things), or None if the model judged the cluster irrelevant. Every
    Turkish field is a literal OCR copy, resolved by index, never model-
    generated text — see module docstring for why that matters here."""
    if not extraction.is_relevant:
        return None

    return {
        "name": _resolve(fragments, extraction.name_index),
        "age": extraction.age,
        "profession": _resolve(fragments, extraction.profession_index),
        "city": _resolve(fragments, extraction.city_index),
        "dishes": [
            {"name": _resolve(fragments, d.name_index) or "", "category": d.category}
            for d in extraction.dishes
        ],
        "scores": [
            {"judge_name": _resolve(fragments, s.judge_name_index) or "", "value": s.value}
            for s in extraction.scores
        ],
    }


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
        transcript_text = transcript.text if transcript else ""

        if not ocr_results:
            return [VisionObservation(
                frame_paths=frame_paths,
                structured={"is_cooking_competition": False, "contestants": []},
            )]

        filtered = filter_persistent_fragments(ocr_results)
        clusters = cluster_by_proximity(filtered)

        partials = [self._extract_cluster(cluster, transcript_text) for cluster in clusters]
        contestants = fuse_cluster_extractions(partials)

        structured = {
            "is_cooking_competition": bool(contestants),
            "contestants": contestants,
        }
        return [VisionObservation(frame_paths=frame_paths, structured=structured)]

    def _extract_cluster(self, cluster: FrameCluster, transcript_text: str) -> Optional[dict]:
        if not cluster.fragments:
            return None

        response = self._client.generate(
            model=self._model,
            prompt=_build_cluster_prompt(transcript_text, cluster.fragments),
            format=_ClusterExtraction.model_json_schema(),
        )

        try:
            extraction = _ClusterExtraction.model_validate_json(response["response"])
        except (KeyError, ValueError):
            return None

        return _resolve_cluster_extraction(extraction, cluster.fragments)
