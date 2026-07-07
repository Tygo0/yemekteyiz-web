from automation.ocr.base import OcrEngine, OcrResult


class MockOcrEngine(OcrEngine):
    """Fakes EasyOCR with canned score-board-style text per frame."""

    def read(self, frame_paths: list[str]) -> list[OcrResult]:
        return [
            OcrResult(frame_path=path, text_lines=["Zuhal: 8", "Somer: 9", "Danilo: 7"])
            for path in frame_paths
        ]
