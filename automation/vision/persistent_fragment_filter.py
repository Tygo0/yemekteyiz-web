"""
Drops OCR fragments that are persistent on-screen noise (a channel logo, the
show's own name/watermark) rather than a specific contestant/dish/score
graphic, before LocalVisionEngine ever sees them.

Discovered against a real episode: EasyOCR on Turkish broadcast footage picks
up the show's watermark ("Zuhal Topal'la Yemekteyiz") in nearly every single
sampled frame for the entire ~90+ minute runtime, and OCR renders it slightly
differently almost every time ("TOPALlA", "TOPAL'LA", "ToPALLA", "topalla",
...). Feeding LocalVisionEngine's un-curated fragment list for a whole episode
produced 351 "contestants" instead of 4 — mostly these watermark variants,
each mistaken for a distinct person by the extraction model. A genuine
contestant/dish/score overlay is only on screen for a narrow window of frames
(while that specific graphic is shown); a watermark is on screen for nearly
all of them. That frame-coverage gap is the signal used here to tell them
apart — not a fixed word/phrase blocklist, since OCR corrupts the same source
text differently on every read, so exact-string matching wouldn't catch most
of the variants.
"""
import difflib
from dataclasses import dataclass

from automation.ocr.base import OcrResult

DEFAULT_MAX_FRAME_COVERAGE_RATIO = 0.3
DEFAULT_SIMILARITY_THRESHOLD = 0.82
# Coverage ratio is meaningless noise with too few samples -- a single frame
# (or a handful, as in a short test clip) makes every fragment "cover" a huge
# share of frames trivially. Below this many frames, skip filtering rather
# than risk wiping out genuine content.
DEFAULT_MIN_FRAMES_TO_FILTER = 10


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


@dataclass
class _FragmentFamily:
    """A cluster of fragments judged near-duplicates of each other (e.g. every
    OCR misread of the same watermark), plus which frames any of them appeared
    in — frame coverage is computed per family, not per exact string, since
    the same source text rarely OCRs identically twice."""

    fragments: set = None
    frames: set = None

    def __post_init__(self):
        self.fragments = self.fragments or set()
        self.frames = self.frames or set()


def filter_persistent_fragments(
    ocr_results: list[OcrResult],
    max_frame_coverage_ratio: float = DEFAULT_MAX_FRAME_COVERAGE_RATIO,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    min_frames_to_filter: int = DEFAULT_MIN_FRAMES_TO_FILTER,
) -> list[OcrResult]:
    """Return ocr_results with persistent-noise fragments removed from every
    frame's text_lines. A fragment is dropped only as part of a whole family —
    if any variant of it is judged a near-duplicate of another variant seen in
    more than max_frame_coverage_ratio of all frames, every variant in that
    family is dropped, everywhere.

    A single contestant's segment can plausibly span a large chunk of a
    multi-contestant episode, so max_frame_coverage_ratio should stay well
    above any one contestant's realistic share (e.g. above 1/4 for a 4-
    contestant week) and well below a true whole-episode watermark's coverage
    (typically near 100%) — the default of 30% sits in that gap.

    Below min_frames_to_filter total frames, filtering is skipped entirely
    (input returned unchanged) — coverage ratios aren't meaningful with only a
    handful of samples, e.g. a short test clip, where any single fragment
    trivially "covers" a large share of frames.
    """
    total_frames = len(ocr_results)
    if total_frames == 0 or total_frames < min_frames_to_filter:
        return ocr_results

    families: list[_FragmentFamily] = []

    for frame_idx, result in enumerate(ocr_results):
        for line in result.text_lines:
            line = line.strip()
            if not line:
                continue
            normalized = _normalize(line)

            match = next(
                (
                    family
                    for family in families
                    if any(
                        difflib.SequenceMatcher(None, normalized, _normalize(existing)).ratio()
                        >= similarity_threshold
                        for existing in family.fragments
                    )
                ),
                None,
            )
            if match is None:
                match = _FragmentFamily()
                families.append(match)
            match.fragments.add(line)
            match.frames.add(frame_idx)

    dropped: set = set()
    for family in families:
        if len(family.frames) / total_frames > max_frame_coverage_ratio:
            dropped |= family.fragments

    if not dropped:
        return ocr_results

    return [
        OcrResult(
            frame_path=result.frame_path,
            text_lines=[line for line in result.text_lines if line.strip() not in dropped],
        )
        for result in ocr_results
    ]
