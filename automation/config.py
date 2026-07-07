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


def get_settings() -> Settings:
    return Settings(
        backend_url=os.environ.get("AUTOMATION_BACKEND_URL", "http://localhost:5000"),
        admin_username=os.environ.get("AUTOMATION_ADMIN_USERNAME", ""),
        admin_password=os.environ.get("AUTOMATION_ADMIN_PASSWORD", ""),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        youtube_channel_url=os.environ.get("AUTOMATION_YOUTUBE_CHANNEL_URL", ""),
    )
