"""
Drops OCR fragments that read like a full-sentence caption/narration (a day
header, a judge's quoted commentary, a prize-money announcement, a host's
narration) rather than a short contestant/dish/judge name, before
LocalVisionEngine's per-cluster classification ever sees them.

Two signals, applied together:

1. Word count. Against a real episode, the per-cluster classifier accepted
   long, sentence-like fragments as "relevant" and pulled a number out of one
   as if it were a judge's score — a caption reading "...TOPLAM 20 PUAN
   ALARAK 200.000 TL'YE VEDA EDIYOR" (a running point total plus a cash-prize
   announcement) produced a "score" of 200000. A genuine contestant/dish/
   judge name is consistently short; word count alone caught most real
   failures. Deliberately not punctuation-based: a colon is also how a
   genuine on-screen score reveal reads ("Zuhal: 8", used throughout this
   project's own mock OCR data), and Turkish possessives/suffixes on real
   names are common ("TOPAL'LA", "YUSUF'A") — punctuation is a weak signal
   here compared to length.

2. Narration vocabulary. OCR sometimes compresses a caption down to 3-4
   words (merging "4.GUN" into one token, dropping a word entirely), landing
   it under the word-count cutoff even though it's still narration, not a
   name card — e.g. "2GUN YARISMACISI POLYANA HOROZ" (a day-header) or
   "YUSUF YARISMACILARIMIZI KARSILIYOR" ("Yusuf greets the contestants").
   These share recognizable host-narration word stems that a genuine name/
   dish/judge fragment doesn't. This is a narrower, show-specific heuristic
   than word count and needs upkeep if the show's wording changes — but the
   words themselves are stable across an episode/season since they're the
   show's own recurring narration vocabulary, not per-contestant content.
   Matching is done after folding Turkish characters to their ASCII
   equivalents, since EasyOCR doesn't always render diacritics correctly.
"""
import re

from automation.ocr.base import OcrResult

DEFAULT_MAX_WORDS = 4

# Word stems for recurring host-narration vocabulary, not per-contestant
# content -- e.g. "YARISMAC" matches "yarismaci/yarismacisi/yarismacilarimizi"
# ("contestant(s)"), all inflected forms of the same narration word.
NARRATION_KEYWORD_ROOTS = (
    "YARISMAC",  # yarismaci(si/lari/mizi) -- "contestant(s)"
    "KARSIL",    # karsiliyor -- "greets/welcomes" (not the bare "karsi" root,
                 # which would false-positive on a real place name like
                 # "Karsiyaka")
    "MENU",      # menusu -- "menu"
    "VEDA",      # veda ediyor -- "bids farewell"
    "TOPLAM",    # toplam ... puan -- "total ... points"
)

# A leading ordinal day marker ("4.GUN", "2GUN") is host narration
# (day-header captions), never a contestant/dish/judge name.
_DAY_HEADER_PATTERN = re.compile(r"\d+\s*\.?\s*GUN", re.IGNORECASE)

_TURKISH_FOLD = str.maketrans({
    "İ": "I", "ı": "i",
    "Ş": "S", "ş": "s",
    "Ç": "C", "ç": "c",
    "Ğ": "G", "ğ": "g",
    "Ö": "O", "ö": "o",
    "Ü": "U", "ü": "u",
})


def _fold_turkish(text: str) -> str:
    return text.translate(_TURKISH_FOLD).upper()


def _looks_like_a_caption(fragment: str, max_words: int) -> bool:
    if len(fragment.split()) > max_words:
        return True
    folded = _fold_turkish(fragment)
    if any(root in folded for root in NARRATION_KEYWORD_ROOTS):
        return True
    return bool(_DAY_HEADER_PATTERN.search(folded))


def filter_caption_like_fragments(
    ocr_results: list[OcrResult],
    max_words: int = DEFAULT_MAX_WORDS,
) -> list[OcrResult]:
    """Return ocr_results with caption/narration-like fragments removed from
    every frame's text_lines. Short fragments free of narration vocabulary
    (names, dish names, ages, cities) are left untouched."""
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
