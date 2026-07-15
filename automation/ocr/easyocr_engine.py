import easyocr
from automation.ocr.base import OcrEngine, OcrResult
from automation.progress import report_progress


class EasyOcrEngine(OcrEngine):
    def __init__(self, languages: list[str] | None = None):
        self._reader = easyocr.Reader(languages or ["tr", "en"])

    def read(self, frame_paths: list[str]) -> list[OcrResult]:
        results = []
        total = len(frame_paths)
        for i, path in enumerate(frame_paths):
            lines = [text for (_bbox, text, _confidence) in self._reader.readtext(path)]
            results.append(OcrResult(frame_path=path, text_lines=lines))
            if (i + 1) % 10 == 0 or i + 1 == total:
                report_progress("  OCR frame", i + 1, total)
        return results
