"""
Unit tests for LocalVisionEngine's deterministic, network-free logic: OCR
fragment collection, index resolution, and prompt building. The actual Ollama
call is exercised separately by a smoke test that requires a running local
model (added alongside the pipeline-wiring step, mirroring test_gemini_smoke.py).
"""
from automation.ocr.base import OcrResult
from automation.vision.local_vision import (
    NO_INDEX,
    _IndexedContestant,
    _IndexedDish,
    _IndexedExtraction,
    _IndexedScore,
    _build_prompt,
    _collect_ocr_fragments,
    _resolve,
    _resolve_extraction,
)


def test_collect_ocr_fragments_deduplicates_and_preserves_order():
    ocr_results = [
        OcrResult(frame_path="f1.jpg", text_lines=["Ayse", "Istanbul", ""]),
        OcrResult(frame_path="f2.jpg", text_lines=["Istanbul", "Mercimek Corbasi"]),
    ]
    assert _collect_ocr_fragments(ocr_results) == ["Ayse", "Istanbul", "Mercimek Corbasi"]


def test_collect_ocr_fragments_handles_empty_input():
    assert _collect_ocr_fragments(None) == []
    assert _collect_ocr_fragments([]) == []


def test_resolve_returns_literal_text_for_valid_index():
    fragments = ["Ayse", "Istanbul", "Zuhal"]
    assert _resolve(fragments, 0) == "Ayse"
    assert _resolve(fragments, 2) == "Zuhal"


def test_resolve_returns_none_for_missing_or_bad_index():
    fragments = ["Ayse", "Istanbul"]
    assert _resolve(fragments, NO_INDEX) is None
    assert _resolve(fragments, None) is None
    assert _resolve(fragments, 99) is None
    assert _resolve(fragments, -5) is None


def test_build_prompt_numbers_fragments_and_embeds_transcript():
    prompt = _build_prompt("A contestant cooks soup.", ["Ayse", "Istanbul"])
    assert "[0] Ayse" in prompt
    assert "[1] Istanbul" in prompt
    assert "A contestant cooks soup." in prompt


def test_build_prompt_handles_no_fragments_or_transcript():
    prompt = _build_prompt("", [])
    assert "(none detected)" in prompt
    assert "(no speech detected)" in prompt


def test_resolve_extraction_returns_empty_when_not_cooking_competition():
    extraction = _IndexedExtraction(is_cooking_competition=False, contestants=[
        _IndexedContestant(name_index=0),
    ])
    result = _resolve_extraction(extraction, ["Ayse"])
    assert result == {"is_cooking_competition": False, "contestants": []}


def test_resolve_extraction_substitutes_literal_ocr_text():
    fragments = ["Ayse", "Istanbul", "Mercimek Corbasi", "Zuhal", "Ogretmen"]
    extraction = _IndexedExtraction(
        is_cooking_competition=True,
        contestants=[
            _IndexedContestant(
                name_index=0,
                age=28,
                profession_index=4,
                city_index=1,
                dishes=[_IndexedDish(name_index=2, category="soup")],
                scores=[_IndexedScore(judge_name_index=3, value=8)],
            )
        ],
    )
    result = _resolve_extraction(extraction, fragments)
    assert result["is_cooking_competition"] is True
    contestant = result["contestants"][0]
    assert contestant["name"] == "Ayse"
    assert contestant["age"] == 28
    assert contestant["profession"] == "Ogretmen"
    assert contestant["city"] == "Istanbul"
    assert contestant["dishes"] == [{"name": "Mercimek Corbasi", "category": "soup"}]
    assert contestant["scores"] == [{"judge_name": "Zuhal", "value": 8}]


def test_resolve_extraction_missing_index_becomes_empty_string_not_crash():
    extraction = _IndexedExtraction(
        is_cooking_competition=True,
        contestants=[_IndexedContestant(name_index=NO_INDEX)],
    )
    result = _resolve_extraction(extraction, ["Ayse"])
    assert result["contestants"][0]["name"] == ""
