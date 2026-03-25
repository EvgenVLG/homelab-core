"""
Compute summary statistics and persist all output artefacts.

Outputs written:
  library_index.csv      — all scanned library tracks
  matched_tracks.csv     — successful matches with score + reason
  unmatched_history.csv  — history entries with no library match
  summary.json           — counts and match rate
"""
from __future__ import annotations
import csv
import json
import logging
from pathlib import Path

from .models import HistoryEntry, LibraryTrack, MatchResult, Stats
from .normalize import normalize

logger = logging.getLogger(__name__)


def compute_stats(
    history: list[HistoryEntry],
    library: list[LibraryTrack],
    matched: list[MatchResult],
    unmatched: list[HistoryEntry],
    playlists: list[str],
) -> Stats:
    unique_keys = {(normalize(e.artist), normalize(e.track)) for e in history}
    return Stats(
        history_entries=len(history),
        unique_history_tracks=len(unique_keys),
        library_tracks=len(library),
        matched=len(matched),
        unmatched=len(unmatched),
        playlists_generated=[Path(p).name for p in playlists],
    )


def save_outputs(
    history: list[HistoryEntry],
    library: list[LibraryTrack],
    matched: list[MatchResult],
    unmatched: list[HistoryEntry],
    playlists: list[str],
    output_dir: str,
) -> Stats:
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)

    # library_index.csv
    with open(base / "library_index.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "artist", "album", "title", "extension"])
        for t in library:
            w.writerow([t.path, t.artist, t.album, t.title, t.extension])
    logger.info("Wrote library_index.csv (%d rows)", len(library))

    # matched_tracks.csv
    with open(base / "matched_tracks.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "history_artist", "history_track", "library_path",
            "library_artist", "library_title", "score", "reason",
        ])
        for m in matched:
            w.writerow([
                m.history_artist, m.history_track, m.library_path,
                m.library_artist, m.library_title, m.score, m.reason,
            ])
    logger.info("Wrote matched_tracks.csv (%d rows)", len(matched))

    # unmatched_history.csv
    with open(base / "unmatched_history.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "artist", "track", "album", "timestamp", "play_count"])
        for e in unmatched:
            w.writerow([e.source, e.artist, e.track, e.album, e.timestamp, e.play_count])
    logger.info("Wrote unmatched_history.csv (%d rows)", len(unmatched))

    stats = compute_stats(history, library, matched, unmatched, playlists)

    match_rate = round(100 * stats.matched / max(stats.unique_history_tracks, 1), 1)

    with open(base / "summary.json", "w", encoding="utf-8") as fh:
        json.dump(
            {
                "history_entries": stats.history_entries,
                "unique_history_tracks": stats.unique_history_tracks,
                "library_tracks": stats.library_tracks,
                "matched": stats.matched,
                "unmatched": stats.unmatched,
                "match_rate_pct": match_rate,
                "playlists_generated": stats.playlists_generated,
            },
            fh,
            indent=2,
        )
    logger.info(
        "Summary: %d/%d matched (%.1f%%) | %d library tracks | %d playlists",
        stats.matched, stats.unique_history_tracks, match_rate,
        stats.library_tracks, len(stats.playlists_generated),
    )

    return stats
