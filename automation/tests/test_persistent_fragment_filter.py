from automation.ocr.base import OcrResult
from automation.vision.persistent_fragment_filter import filter_persistent_fragments


def _frames(*lines_per_frame: list[str]) -> list[OcrResult]:
    return [OcrResult(frame_path=f"frame_{i}.jpg", text_lines=lines) for i, lines in enumerate(lines_per_frame)]


def test_empty_input_returns_as_is():
    assert filter_persistent_fragments([]) == []


def test_rare_fragment_is_kept():
    # A dish name appearing in only 1 of 10 frames should survive.
    ocr_results = _frames(*([["Mercimek Corbasi"]] + [[] for _ in range(9)]))
    result = filter_persistent_fragments(ocr_results)
    assert result[0].text_lines == ["Mercimek Corbasi"]


def test_watermark_appearing_in_every_frame_is_dropped():
    # Same literal string in all 10 frames -- clearly persistent noise.
    ocr_results = _frames(*[["Yemekteyiz"] for _ in range(10)])
    result = filter_persistent_fragments(ocr_results)
    assert all(f.text_lines == [] for f in result)


def test_watermark_with_ocr_noise_variants_is_still_dropped():
    # Real-world case: the same watermark OCRs slightly differently almost
    # every frame. Exact-string matching would miss this entirely; fuzzy
    # matching should still recognize them as one family and drop all of them.
    # Every pairwise similarity among these 5 is >= 0.857, so they cluster
    # into one family regardless of set-iteration order.
    variants = ["TOPALlA", "ToPALLA", "topalla", "TOPALLa", "TOPALIA"]
    # 5 of 9 frames (~56%) carry a watermark variant -- well over the 30%
    # threshold -- the other 4 have unrelated, unique one-off content.
    ocr_results = _frames(*[[v] for v in variants], *[[f"unrelated_{i}"] for i in range(4)])
    result = filter_persistent_fragments(ocr_results, max_frame_coverage_ratio=0.3)
    assert all(v not in f.text_lines for f in result for v in variants)


def test_contestant_specific_content_survives_alongside_dropped_watermark():
    # A watermark in every frame, plus a dish name that only shows up briefly
    # in one frame -- only the watermark should be dropped.
    ocr_results = _frames(
        ["Yemekteyiz", "Mercimek Corbasi"],
        ["Yemekteyiz"],
        ["Yemekteyiz"],
        ["Yemekteyiz"],
    )
    result = filter_persistent_fragments(ocr_results)
    assert result[0].text_lines == ["Mercimek Corbasi"]
    assert all("Yemekteyiz" not in f.text_lines for f in result)


def test_fragment_just_under_coverage_threshold_is_kept():
    # 3 of 10 frames = 30% coverage, not strictly greater than a 0.3 threshold.
    ocr_results = _frames(*([["Ayse"]] * 3 + [[] for _ in range(7)]))
    result = filter_persistent_fragments(ocr_results, max_frame_coverage_ratio=0.3)
    assert result[0].text_lines == ["Ayse"]


def test_fragment_over_coverage_threshold_is_dropped():
    # 4 of 10 frames = 40% coverage, over a 0.3 threshold.
    ocr_results = _frames(*([["Ayse"]] * 4 + [[] for _ in range(6)]))
    result = filter_persistent_fragments(ocr_results, max_frame_coverage_ratio=0.3)
    assert all(f.text_lines == [] for f in result)


def test_dissimilar_fragments_are_not_merged_into_one_family():
    ocr_results = _frames(["Ayse"], ["Mehmet"], ["Fatma"], ["Ali"])
    result = filter_persistent_fragments(ocr_results)
    assert [f.text_lines for f in result] == [["Ayse"], ["Mehmet"], ["Fatma"], ["Ali"]]
