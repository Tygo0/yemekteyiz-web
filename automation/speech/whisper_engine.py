import whisper
from automation.speech.base import SpeechEngine, Transcript


class WhisperSpeechEngine(SpeechEngine):
    def __init__(self, model_name: str = "base"):
        self._model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str, task: str = "translate") -> Transcript:
        result = self._model.transcribe(audio_path, language="tr", task=task)
        segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
            for seg in result.get("segments", [])
        ]
        return Transcript(text=result.get("text", ""), segments=segments)
