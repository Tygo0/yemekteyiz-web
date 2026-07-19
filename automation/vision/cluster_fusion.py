"""
Merges LocalVisionEngine's per-cluster extractions (one dict per FrameCluster,
or None for an irrelevant cluster) into a final contestants list.

A single on-screen graphic rarely shows everything about a contestant at
once — a name card shows name/age/profession/city, a separate dish overlay
shows just a dish, a separate score reveal shows just a judge+value, with no
name repeated on it. Clusters are walked in temporal order (the order
FrameCluster.cluster_by_proximity already returns them in) and a "current
contestant" is tracked: a cluster with its own name either starts a new
contestant or, if it fuzzy-matches an already-seen name (OCR renders the same
name slightly differently card to card), merges into that existing record and
becomes current. A cluster with no name of its own attaches its dishes/scores
to whichever contestant is currently current, on the assumption that a
show's per-contestant segments play out consecutively (name intro -> dish
reveal -> judging) rather than interleaved.
"""
import difflib
from typing import Optional

NAME_MATCH_SIMILARITY_THRESHOLD = 0.75


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _names_match(a: str, b: str, threshold: float = NAME_MATCH_SIMILARITY_THRESHOLD) -> bool:
    return difflib.SequenceMatcher(None, _normalize(a), _normalize(b)).ratio() >= threshold


def fuse_cluster_extractions(partials: list[Optional[dict]]) -> list[dict]:
    """partials: one dict per cluster (name/age/profession/city/dishes/scores,
    any of which may be None/empty) in temporal order, or None for a cluster
    judged irrelevant. Returns the final contestants list in the same shape
    GeminiVisionEngine.analyze() produces."""
    contestants: list[dict] = []
    current_index: Optional[int] = None

    for partial in partials:
        if partial is None:
            continue

        name = partial.get("name")
        dishes = list(partial.get("dishes") or [])
        scores = list(partial.get("scores") or [])

        if name:
            match_index = next(
                (i for i, c in enumerate(contestants) if _names_match(c["name"], name)),
                None,
            )
            if match_index is None:
                contestants.append({
                    "name": name,
                    "age": partial.get("age"),
                    "profession": partial.get("profession"),
                    "city": partial.get("city"),
                    "dishes": dishes,
                    "scores": scores,
                })
                current_index = len(contestants) - 1
            else:
                existing = contestants[match_index]
                if existing["age"] is None:
                    existing["age"] = partial.get("age")
                existing["profession"] = existing["profession"] or partial.get("profession")
                existing["city"] = existing["city"] or partial.get("city")
                existing["dishes"].extend(dishes)
                existing["scores"].extend(scores)
                current_index = match_index
        elif current_index is not None:
            contestants[current_index]["dishes"].extend(dishes)
            contestants[current_index]["scores"].extend(scores)
        # else: dishes/scores with no name established yet anywhere -- can't
        # attribute them to anyone, so they're dropped rather than guessed at.

    return contestants
