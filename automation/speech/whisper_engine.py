import whisper
from automation.speech.base import SpeechEngine, Transcript
from automation.progress import report


class WhisperSpeechEngine(SpeechEngine):
    def __init__(self, model_name: str = "base"):
        self._model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str, task: str = "translate") -> Transcript:
        report("  (Whisper progress bar below tracks decoded audio frames)")
        # verbose=False (not the default None) is what actually enables
        # whisper's own tqdm progress bar instead of staying silent —
        # counterintuitive, but confirmed against the installed package's
        # source: the bar is disabled unless verbose is exactly False.
        result = self._model.transcribe(audio_path, language="tr", task=task, verbose=False)
        segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
            for seg in result.get("segments", [])
        ]
        return Transcript(text=result.get("text", ""), segments=segments)
