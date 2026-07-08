"""
Fuses the pipeline's per-stage outputs into one structured WeekImportPayload.

Vision (Gemini, prompted for JSON) is the primary source of truth for
contestant names, dishes, and scores — it's the one stage that natively
understands the full multi-frame scoreboard. OCR and speech transcripts are
run and available on the PipelineRun for debugging/future corroboration, but
are not yet cross-checked against vision's output; that heuristic is left for
once real footage shows where vision actually gets it wrong.
"""
from datetime import date
from automation.models import WeekImportPayload, ContestantData, DishData, ScoreData
from automation.vision.base import VisionObservation


class VisionRefusalError(Exception):
    """Raised when the vision stage honestly reports the video isn't a
    recognizable cooking competition episode, instead of fabricating
    plausible-looking contestants for content that isn't actually there."""


def fuse(
    week_id: int,
    video_url: str,
    broadcast_date: date | None,
    vision_observations: list[VisionObservation],
) -> WeekImportPayload:
    if not vision_observations:
        raise ValueError("No vision observations to fuse")

    structured = vision_observations[0].structured

    if not structured.get("is_cooking_competition", True):
        raise VisionRefusalError(
            "Vision model determined this video does not show a recognizable "
            "cooking competition episode — skipping import rather than "
            "fabricating contestant data."
        )

    contestants_raw = structured.get("contestants", [])

    contestants = [
        ContestantData(
            name=c["name"],
            age=c.get("age"),
            profession=c.get("profession"),
            city=c.get("city"),
            biography=c.get("biography"),
            photo_url=c.get("photo_url"),
            broadcast_date=broadcast_date,
            video_url=video_url,
            dishes=[DishData(name=d["name"], category=d["category"]) for d in c.get("dishes", [])],
            scores=[ScoreData(judge_name=s["judge_name"], value=s["value"]) for s in c.get("scores", [])],
        )
        for c in contestants_raw
    ]

    return WeekImportPayload(week_id=week_id, contestants=contestants)
