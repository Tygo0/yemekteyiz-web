"""
Minimal progress reporting for the automation pipeline. Plain flushed prints
rather than a logging framework — this exists specifically so a long-running
CLI run (e.g. `python -m automation.cli`, piped to a file when run in the
background) shows *something* checkable while it's working, after a real run
against a full episode sat silent for ~2 hours with only two warning lines in
the whole log and no way to tell whether it was still making progress.
"""


def report(message: str) -> None:
    print(f"[automation] {message}", flush=True)


def report_progress(stage: str, current: int, total: int) -> None:
    percent = (current / total * 100) if total else 0
    report(f"{stage}: {current}/{total} ({percent:.0f}%)")
