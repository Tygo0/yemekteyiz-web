from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DownloadedVideo:
    video_path: str
    source_url: str
    title: str


class Downloader(ABC):
    @abstractmethod
    def list_new_videos(self, channel_url: str) -> list[str]:
        """Return URLs of videos on the channel not yet processed."""

    @abstractmethod
    def download(self, video_url: str, dest_dir: str) -> DownloadedVideo:
        """Download a video and return its local path."""
