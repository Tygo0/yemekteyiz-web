import easyocr
from automation.ocr.base import OcrEngine, OcrResult


class EasyOcrEngine(OcrEngine):
    def __init__(self, languages: list[str] | None = None):
        self._reader = easyocr.Reader(languages or ["tr", "en"])

    def read(self, frame_paths: list[str]) -> list[OcrResult]:
        results = []
        for path in frame_paths:
            lines = [text for (_bbox, text, _confidence) in self._reader.readtext(path)]
            results.append(OcrResult(frame_path=path, text_lines=lines))
        return results
