"""
Cron-style polling stub: periodically asks the downloader for new videos on
the channel and runs the pipeline for each one not seen before. `week_id_for`
is injected because matching a new video to the right (already admin-created)
week is a business decision outside the scheduler's concern.
"""
import time
import logging
from typing import Callable
from automation.pipeline import Pipeline

logger = logging.getLogger(__name__)


class Poller:
    def __init__(self, pipeline: Pipeline, channel_url: str, week_id_for: Callable[[str], int | None]):
        self.pipeline = pipeline
        self.channel_url = channel_url
        self.week_id_for = week_id_for
        self._seen: set[str] = set()

    def poll_once(self) -> None:
        for video_url in self.pipeline.downloader.list_new_videos(self.channel_url):
            if video_url in self._seen:
                continue
            self._seen.add(video_url)

            week_id = self.week_id_for(video_url)
            if week_id is None:
                logger.warning("No matching week for video %s, skipping", video_url)
                continue

            try:
                self.pipeline.run(video_url, week_id)
                logger.info("Imported %s into week %s", video_url, week_id)
            except Exception:
                logger.exception("Failed to process %s", video_url)

    def run_forever(self, interval_seconds: int = 600) -> None:
        while True:
            self.poll_once()
            time.sleep(interval_seconds)
