"""
Drops OCR fragments that read like a full-sentence caption/narration (a day
header, a judge's quoted commentary, a prize-money announcement) rather than
a short contestant/dish/judge name, before LocalVisionEngine's per-cluster
classification ever sees them.

Against a real episode, the per-cluster classifier accepted long, sentence-
like fragments as "relevant" and pulled a number out of them as if it were a
judge's score — a caption reading "...TOPLAM 20 PUAN ALARAK 200.000 TL'YE
VEDA EDIYOR" (a running point total plus a cash-prize announcement) produced
a "score" of 200000, later attributed to whichever contestant happened to be
current at that point in the episode (see cluster_fusion). A genuine
contestant/dish/judge name is consistently short (a handful of words at
most); a narration caption reads like a sentence — word count alone is
enough to tell the two apart for every real failure case seen so far.

Deliberately word-count-only, not punctuation-based: a colon is also how a
genuine on-screen score reveal reads ("Zuhal: 8", used throughout this
project's own mock/synthetic OCR data), so disqualifying fragments containing
a colon would drop real score fragments right alongside the captions it's
meant to catch. Turkish possessives/suffixes on real names are also common
("TOPAL'LA", "YUSUF'A"), so punctuation in general is a weak signal here
compared to length.
"""
from automation.ocr.base import OcrResult

DEFAULT_MAX_WORDS = 4


def _looks_like_a_caption(fragment: str, max_words: int) -> bool:
    return len(fragment.split()) > max_words


def filter_caption_like_fragments(
    ocr_results: list[OcrResult],
    max_words: int = DEFAULT_MAX_WORDS,
) -> list[OcrResult]:
    """Return ocr_results with sentence-like fragments removed from every
    frame's text_lines. Short fragments (names, dish names, ages, cities) are
    left untouched."""
    return [
        OcrResult(
            frame_path=result.frame_path,
            text_lines=[
                line for line in result.text_lines
                if line.strip() and not _looks_like_a_caption(line.strip(), max_words)
            ],
        )
        for result in ocr_results
    ]
