from automation.speech.base import SpeechEngine, Transcript


class MockSpeechEngine(SpeechEngine):
    """Fakes Whisper with a canned transcript."""

    def transcribe(self, audio_path: str, task: str = "translate") -> Transcript:
        text = "Zuhal verdi sekiz, Somer verdi dokuz, Danilo verdi yedi."
        return Transcript(text=text, segments=[{"start": 0.0, "end": 3.0, "text": text}])
