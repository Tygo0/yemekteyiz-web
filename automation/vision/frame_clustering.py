"""
Groups a video's (already watermark-filtered) per-frame OCR results into
temporal clusters, each representing one on-screen graphic — a contestant
name card, a dish overlay, a score reveal — rather than treating either the
whole episode's fragments as one flat pool (which produced 351 "contestants"
from one real episode) or every single frame as its own isolated unit
(which would split one card shown across several consecutive sampled frames
into redundant duplicate extraction calls).

Frames are sampled at a fixed interval (see FfmpegExtractor), so temporal
order is just frame index order. Consecutive frames whose OCR fragments
overlap (fuzzy-matched, for the same OCR-noise reasons as
persistent_fragment_filter) are taken to be showing the same graphic and are
merged into one cluster; a short run of frames with no surviving fragments
doesn't necessarily end a cluster, since the same graphic can still be on
screen while OCR happens to miss it in a particular sampled frame.
"""
import difflib
from dataclasses import dataclass, field

from automation.ocr.base import OcrResult

DEFAULT_SIMILARITY_THRESHOLD = 0.75
DEFAULT_MAX_EMPTY_GAP = 1


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


@dataclass
class FrameCluster:
    frame_indices: list = field(default_factory=list)
    fragments: list = field(default_factory=list)  # deduped, order-preserving


def _fuzzy_overlaps(fragments: list, normalized_pool: set, threshold: float) -> bool:
    return any(
        difflib.SequenceMatcher(None, _normalize(frag), existing).ratio() >= threshold
        for frag in fragments
        for existing in normalized_pool
    )


def cluster_by_proximity(
    ocr_results: list[OcrResult],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    max_empty_gap: int = DEFAULT_MAX_EMPTY_GAP,
) -> list[FrameCluster]:
    clusters: list[FrameCluster] = []
    current: FrameCluster | None = None
    current_normalized: set = set()
    empty_streak = 0

    def _close_current():
        nonlocal current, current_normalized, empty_streak
        if current is not None:
            clusters.append(current)
        current = None
        current_normalized = set()
        empty_streak = 0

    def _start(idx: int, fragments: list):
        nonlocal current, current_normalized
        current = FrameCluster(frame_indices=[idx], fragments=list(dict.fromkeys(fragments)))
        current_normalized = {_normalize(f) for f in fragments}

    def _merge(idx: int, fragments: list):
        current.frame_indices.append(idx)
        for frag in fragments:
            if frag not in current.fragments:
                current.fragments.append(frag)
                current_normalized.add(_normalize(frag))

    for idx, result in enumerate(ocr_results):
        fragments = [line.strip() for line in result.text_lines if line.strip()]

        if not fragments:
            if current is not None:
                empty_streak += 1
                if empty_streak > max_empty_gap:
                    _close_current()
            continue

        empty_streak = 0
        if current is None:
            _start(idx, fragments)
        elif _fuzzy_overlaps(fragments, current_normalized, similarity_threshold):
            _merge(idx, fragments)
        else:
            _close_current()
            _start(idx, fragments)

    _close_current()
    return clusters
