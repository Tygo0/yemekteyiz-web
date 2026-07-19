from automation.ocr.base import OcrResult
from automation.vision.frame_clustering import cluster_by_proximity


def _frames(*lines_per_frame: list[str]) -> list[OcrResult]:
    return [OcrResult(frame_path=f"frame_{i}.jpg", text_lines=lines) for i, lines in enumerate(lines_per_frame)]


def test_empty_input_returns_no_clusters():
    assert cluster_by_proximity([]) == []


def test_single_frame_with_content_is_one_cluster():
    clusters = cluster_by_proximity(_frames(["Ayse"]))
    assert len(clusters) == 1
    assert clusters[0].frame_indices == [0]
    assert clusters[0].fragments == ["Ayse"]


def test_all_empty_frames_produce_no_clusters():
    clusters = cluster_by_proximity(_frames([], [], []))
    assert clusters == []


def test_consecutive_frames_with_overlapping_content_merge_into_one_cluster():
    # Same name card OCR'd slightly differently across 3 consecutive frames.
    clusters = cluster_by_proximity(_frames(["Ayse", "Istanbul"], ["Ayse", "Ogretmen"], ["Ayse"]))
    assert len(clusters) == 1
    assert clusters[0].frame_indices == [0, 1, 2]
    assert clusters[0].fragments == ["Ayse", "Istanbul", "Ogretmen"]


def test_unrelated_consecutive_frames_form_separate_clusters():
    clusters = cluster_by_proximity(_frames(["Ayse card info"], ["Mercimek Corbasi dish"]))
    assert len(clusters) == 2
    assert clusters[0].fragments == ["Ayse card info"]
    assert clusters[1].fragments == ["Mercimek Corbasi dish"]


def test_single_empty_frame_gap_is_bridged_by_default():
    # Same card, but OCR missed it entirely on the middle sampled frame.
    clusters = cluster_by_proximity(_frames(["Ayse"], [], ["Ayse"]), max_empty_gap=1)
    assert len(clusters) == 1
    assert clusters[0].frame_indices == [0, 2]


def test_empty_gap_beyond_max_splits_into_separate_clusters():
    clusters = cluster_by_proximity(_frames(["Ayse"], [], [], ["Ayse"]), max_empty_gap=1)
    assert len(clusters) == 2
    assert clusters[0].frame_indices == [0]
    assert clusters[1].frame_indices == [3]


def test_fragments_within_a_cluster_are_deduplicated_and_order_preserved():
    clusters = cluster_by_proximity(_frames(["Ayse", "Istanbul"], ["Istanbul", "Ayse"]))
    assert clusters[0].fragments == ["Ayse", "Istanbul"]


def test_trailing_open_cluster_is_still_returned():
    # Regression guard: a cluster still open at the end of the frame list
    # (no trailing empty-frame gap to close it) must still be emitted.
    clusters = cluster_by_proximity(_frames(["Ayse"], ["Ayse"]))
    assert len(clusters) == 1
    assert clusters[0].frame_indices == [0, 1]
