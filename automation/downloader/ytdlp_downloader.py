import os
import yt_dlp
from automation.downloader.base import Downloader, DownloadedVideo


class YtDlpDownloader(Downloader):
    def list_new_videos(self, channel_url: str) -> list[str]:
        opts = {"extract_flat": True, "quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
        entries = info.get("entries", []) if info else []
        return [entry["url"] for entry in entries if entry.get("url")]

    def download(self, video_url: str, dest_dir: str) -> DownloadedVideo:
        os.makedirs(dest_dir, exist_ok=True)
        opts = {
            "outtmpl": os.path.join(dest_dir, "%(id)s.%(ext)s"),
            "format": "best[ext=mp4]/best",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_path = ydl.prepare_filename(info)

        return DownloadedVideo(video_path=video_path, source_url=video_url, title=info.get("title", ""))
