import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    backend_url: str
    admin_username: str
    admin_password: str
    gemini_api_key: str
    youtube_channel_url: str
    vision_engine: str
    ollama_model: str
    ollama_host: str


def get_settings() -> Settings:
    return Settings(
        backend_url=os.environ.get("AUTOMATION_BACKEND_URL", "http://localhost:5000"),
        admin_username=os.environ.get("AUTOMATION_ADMIN_USERNAME", ""),
        admin_password=os.environ.get("AUTOMATION_ADMIN_PASSWORD", ""),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        youtube_channel_url=os.environ.get("AUTOMATION_YOUTUBE_CHANNEL_URL", ""),
        # "gemini" (default, hosted) or "local" (Ollama, no external API calls) —
        # see automation/vision/local_vision.py for what the local engine trades off.
        vision_engine=os.environ.get("AUTOMATION_VISION_ENGINE", "gemini"),
        ollama_model=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_K_M"),
        ollama_host=os.environ.get("OLLAMA_HOST", ""),
    )
