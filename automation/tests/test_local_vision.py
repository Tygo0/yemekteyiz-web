"""
Unit tests for LocalVisionEngine's deterministic, network-free logic: index
resolution, per-cluster prompt building, and turning one cluster's model
output into a partial contestant dict. The actual Ollama call is exercised
separately by a smoke test that requires a running local model
(test_local_vision_smoke.py). Persistent-fragment filtering, frame
clustering, and cross-cluster fusion each have their own dedicated test
files (test_persistent_fragment_filter.py, test_frame_clustering.py,
test_cluster_fusion.py) since LocalVisionEngine only orchestrates them.
"""
from automation.vision.local_vision import (
    NO_INDEX,
    _ClusterDish,
    _ClusterExtraction,
    _ClusterScore,
    _build_cluster_prompt,
    _resolve,
    _resolve_cluster_extraction,
)


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


def test_build_cluster_prompt_numbers_fragments_and_embeds_transcript():
    prompt = _build_cluster_prompt("A contestant cooks soup.", ["Ayse", "Istanbul"])
    assert "[0] Ayse" in prompt
    assert "[1] Istanbul" in prompt
    assert "A contestant cooks soup." in prompt


def test_build_cluster_prompt_handles_no_fragments_or_transcript():
    prompt = _build_cluster_prompt("", [])
    assert "(none detected)" in prompt
    assert "(no speech detected)" in prompt


def test_resolve_cluster_extraction_returns_none_when_not_relevant():
    extraction = _ClusterExtraction(is_relevant=False, name_index=0)
    assert _resolve_cluster_extraction(extraction, ["Ayse"]) is None


def test_resolve_cluster_extraction_substitutes_literal_ocr_text():
    fragments = ["Ayse", "Istanbul", "Mercimek Corbasi", "Zuhal", "Ogretmen"]
    extraction = _ClusterExtraction(
        is_relevant=True,
        name_index=0,
        age=28,
        profession_index=4,
        city_index=1,
        dishes=[_ClusterDish(name_index=2, category="soup")],
        scores=[_ClusterScore(judge_name_index=3, value=8)],
    )
    result = _resolve_cluster_extraction(extraction, fragments)
    assert result["name"] == "Ayse"
    assert result["age"] == 28
    assert result["profession"] == "Ogretmen"
    assert result["city"] == "Istanbul"
    assert result["dishes"] == [{"name": "Mercimek Corbasi", "category": "soup"}]
    assert result["scores"] == [{"judge_name": "Zuhal", "value": 8}]


def test_resolve_cluster_extraction_missing_name_becomes_none_not_crash():
    extraction = _ClusterExtraction(is_relevant=True, name_index=NO_INDEX)
    result = _resolve_cluster_extraction(extraction, ["Ayse"])
    assert result["name"] is None


def test_resolve_cluster_extraction_allows_partial_fields_only():
    # A dish-only overlay: no name/age/profession/city, just a dish.
    fragments = ["Mercimek Corbasi"]
    extraction = _ClusterExtraction(
        is_relevant=True,
        dishes=[_ClusterDish(name_index=0, category="soup")],
    )
    result = _resolve_cluster_extraction(extraction, fragments)
    assert result["name"] is None
    assert result["dishes"] == [{"name": "Mercimek Corbasi", "category": "soup"}]
    assert result["scores"] == []
