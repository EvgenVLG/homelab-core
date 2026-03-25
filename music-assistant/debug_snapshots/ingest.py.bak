"""
Read listening-history files from INPUT_DIR.

Supported formats
-----------------
1. Google Takeout YouTube Music JSON (watch-history.json style)
2. Generic JSON array with keys: artist, track/title, album, timestamp, play_count
3. CSV with columns: artist, track/title, album, timestamp, play_count

A file that fails to parse is logged and skipped — it never crashes the run.
"""
from __future__ import annotations
import csv
import json
import logging
import re
from pathlib import Path

from .models import HistoryEntry

logger = logging.getLogger(__name__)


# ── internal parsers ─────────────────────────────────────────────────────────

def _parse_google_takeout(data: list[dict]) -> list[HistoryEntry]:
    """
    Google Takeout watch-history.json schema:
      [{
        "header": "YouTube Music",
        "title": "Watched <song title>",
        "subtitles": [{"name": "<artist>", "url": "..."}],
        "time": "2023-04-01T12:00:00.000Z"
      }]
    """
    entries: list[HistoryEntry] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        raw_title: str = item.get("title", "")
        # Strip "Watched " / "Listened to " navigation prefixes
        track = re.sub(
            r"^(?:Watched|Listened to)\s+", "", raw_title, flags=re.IGNORECASE
        ).strip()
        subtitles = item.get("subtitles") or []
        artist = subtitles[0].get("name", "") if subtitles else ""
        timestamp = item.get("time", "")
        if not (artist or track):
            continue
        entries.append(
            HistoryEntry(
                source="google_takeout",
                artist=artist,
                track=track,
                timestamp=timestamp,
                raw_text=raw_title,
            )
        )
    return entries


def _parse_generic_json(data: list[dict]) -> list[HistoryEntry]:
    entries: list[HistoryEntry] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        artist = str(item.get("artist") or item.get("Artist") or "").strip()
        track = str(
            item.get("track") or item.get("title") or
            item.get("Track") or item.get("Title") or ""
        ).strip()
        if not (artist or track):
            continue
        entries.append(
            HistoryEntry(
                source="json",
                artist=artist,
                track=track,
                album=str(item.get("album") or item.get("Album") or "").strip(),
                timestamp=str(item.get("timestamp") or item.get("time") or "").strip(),
                play_count=int(item.get("play_count") or item.get("plays") or 1),
                raw_text=json.dumps(item),
            )
        )
    return entries


def _parse_json_file(path: Path) -> list[HistoryEntry]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        logger.warning(
            "%s: expected a JSON array, got %s — skipping",
            path.name, type(data).__name__,
        )
        return []
    # Google Takeout items always have a "header" key
    if data and isinstance(data[0], dict) and "header" in data[0]:
        return _parse_google_takeout(data)
    return _parse_generic_json(data)


def _parse_csv(path: Path) -> list[HistoryEntry]:
    entries: list[HistoryEntry] = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            artist = (
                row.get("artist") or row.get("Artist") or row.get("ARTIST") or ""
            ).strip()
            track = (
                row.get("track") or row.get("Track") or row.get("TRACK") or
                row.get("title") or row.get("Title") or ""
            ).strip()
            if not (artist or track):
                continue
            try:
                play_count = int(
                    row.get("play_count") or row.get("plays") or row.get("count") or 1
                )
            except (ValueError, TypeError):
                play_count = 1
            entries.append(
                HistoryEntry(
                    source="csv",
                    artist=artist,
                    track=track,
                    album=(row.get("album") or row.get("Album") or "").strip(),
                    timestamp=(
                        row.get("timestamp") or row.get("time") or row.get("date") or ""
                    ).strip(),
                    play_count=play_count,
                    raw_text=str(row),
                )
            )
    return entries


# ── public API ────────────────────────────────────────────────────────────────

def ingest(input_dir: str) -> list[HistoryEntry]:
    """Read all supported files in input_dir and return combined history."""
    entries: list[HistoryEntry] = []
    base = Path(input_dir)

    if not base.exists():
        logger.error("Input directory does not exist: %s", input_dir)
        return entries

    files = sorted(f for f in base.iterdir() if f.is_file())
    if not files:
        logger.warning("Input directory is empty: %s", input_dir)
        return entries

    for fp in files:
        suffix = fp.suffix.lower()
        try:
            if suffix == ".json":
                batch = _parse_json_file(fp)
            elif suffix == ".csv":
                batch = _parse_csv(fp)
            else:
                logger.debug("Skipping unsupported file type: %s", fp.name)
                continue
            logger.info("Ingested %d entries from %s", len(batch), fp.name)
            entries.extend(batch)
        except Exception as exc:
            logger.warning("Failed to parse %s: %s — skipping", fp.name, exc)

    logger.info("Total history entries loaded: %d", len(entries))
    return entries
