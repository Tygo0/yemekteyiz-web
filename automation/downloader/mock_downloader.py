import os
from automation.downloader.base import Downloader, DownloadedVideo


class MockDownloader(Downloader):
    """Fakes yt-dlp: no network access, just touches an empty file so the
    rest of the pipeline has a real path to work with."""

    def __init__(self, new_videos: list[str] | None = None):
        self._new_videos = new_videos if new_videos is not None else [
            "https://youtube.com/watch?v=mock1"
        ]

    def list_new_videos(self, channel_url: str) -> list[str]:
        return list(self._new_videos)

    def download(self, video_url: str, dest_dir: str) -> DownloadedVideo:
        os.makedirs(dest_dir, exist_ok=True)
        video_path = os.path.join(dest_dir, "mock_video.mp4")
        with open(video_path, "wb"):
            pass
        return DownloadedVideo(video_path=video_path, source_url=video_url, title="Mock Episode")
