"""
Playlist generators. Each returns a Path to the written .m3u file.

Heuristics are intentionally simple and transparent.

  listen_again   — most-played matched tracks (sorted by play_count desc)
  favorites      — play_count in the top 25% of matched tracks
  rediscovery    — matched tracks not played in the last REDISCOVERY_DAYS days
  fresh_rotation — library tracks that never appeared in history (shuffled)
  energy_mix     — proxy energy score: genre folder keywords + repeat-play bonus
"""
from __future__ import annotations
import logging
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .models import HistoryEntry, LibraryTrack, MatchResult
from .normalize import normalize

logger = logging.getLogger(__name__)

# Keywords that raise or lower the energy proxy score
_ENERGY_POSITIVE = frozenset([
    "dance", "electronic", "edm", "hip-hop", "hip hop", "hiphop",
    "punk", "metal", "rock", "pop", "funk", "drum",
])
_ENERGY_NEGATIVE = frozenset([
    "live", "acoustic", "classical", "ambient", "sleep",
    "meditation", "jazz", "instrumental",
])


# ── helpers ───────────────────────────────────────────────────────────────────

def _write_m3u(paths: list[str], dest: Path, name: str) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{name}.m3u"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("#EXTM3U\n")
        for p in paths:
            fh.write(f"{p}\n")
    logger.info("Wrote %s (%d tracks)", out.name, len(paths))
    return out


def _parse_ts(ts: str) -> datetime | None:
    """Try several common timestamp formats; return None if unparseable."""
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _play_counts(
    matched: list[MatchResult],
    history: list[HistoryEntry],
) -> dict[str, int]:
    """Map library_path → summed play_count from history."""
    h_counts: dict[tuple[str, str], int] = {}
    for e in history:
        key = (normalize(e.artist), normalize(e.track))
        h_counts[key] = h_counts.get(key, 0) + e.play_count

    counts: dict[str, int] = {}
    for m in matched:
        key = (normalize(m.history_artist), normalize(m.history_track))
        counts[m.library_path] = h_counts.get(key, 1)
    return counts


# ── generators ────────────────────────────────────────────────────────────────

def generate_listen_again(
    matched: list[MatchResult],
    history: list[HistoryEntry],
    size: int,
    output_dir: Path,
) -> Path:
    counts = _play_counts(matched, history)
    paths = sorted(counts, key=lambda p: counts[p], reverse=True)[:size]
    return _write_m3u(paths, output_dir, "listen_again")


def generate_favorites(
    matched: list[MatchResult],
    history: list[HistoryEntry],
    size: int,
    output_dir: Path,
) -> Path:
    counts = _play_counts(matched, history)
    if not counts:
        return _write_m3u([], output_dir, "favorites")
    values = sorted(counts.values(), reverse=True)
    # Top quartile threshold
    cutoff = values[max(0, len(values) // 4)]
    favs = [p for p, c in counts.items() if c >= cutoff][:size]
    return _write_m3u(favs, output_dir, "favorites")


def generate_rediscovery(
    matched: list[MatchResult],
    history: list[HistoryEntry],
    size: int,
    rediscovery_days: int,
    output_dir: Path,
) -> Path:
    """Tracks that were played historically but not in the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=rediscovery_days)

    last_played: dict[tuple[str, str], datetime] = {}
    for e in history:
        ts = _parse_ts(e.timestamp)
        if ts is None:
            continue
        key = (normalize(e.artist), normalize(e.track))
        if key not in last_played or ts > last_played[key]:
            last_played[key] = ts

    paths: list[str] = []
    for m in matched:
        key = (normalize(m.history_artist), normalize(m.history_track))
        lp = last_played.get(key)
        # Include if: no timestamp at all (can't tell recency) OR last play was old
        if lp is None or lp < cutoff:
            paths.append(m.library_path)

    random.shuffle(paths)
    return _write_m3u(paths[:size], output_dir, "rediscovery")


def generate_fresh_rotation(
    matched: list[MatchResult],
    library: list[LibraryTrack],
    size: int,
    output_dir: Path,
) -> Path:
    """Library tracks that never appeared in listening history."""
    matched_paths = {m.library_path for m in matched}
    fresh = [t.path for t in library if t.path not in matched_paths]
    random.shuffle(fresh)
    return _write_m3u(fresh[:size], output_dir, "fresh_rotation")


def generate_energy_mix(
    matched: list[MatchResult],
    library: list[LibraryTrack],
    history: list[HistoryEntry],
    size: int,
    output_dir: Path,
) -> Path:
    """
    Proxy energy score per track:
      +1 per energy-positive keyword found in path (genre folder names)
      -2 per energy-negative keyword found in path
      +0–1 bonus for repeat-play history

    Falls back to most-played matched tracks if too few score positively.
    """
    counts = _play_counts(matched, history)

    def _score(track: LibraryTrack) -> float:
        path_low = track.path.lower()
        s = 0.0
        for kw in _ENERGY_POSITIVE:
            if kw in path_low:
                s += 1.0
        for kw in _ENERGY_NEGATIVE:
            if kw in path_low:
                s -= 2.0
        plays = counts.get(track.path, 0)
        s += min(plays * 0.2, 1.0)
        return s

    scored = sorted(library, key=_score, reverse=True)
    paths = [t.path for t in scored if _score(t) > 0][:size]

    if len(paths) < size // 2:
        logger.debug(
            "energy_mix: only %d scored positively, falling back to listen_again order",
            len(paths),
        )
        paths = sorted(counts, key=lambda p: counts[p], reverse=True)[:size]

    return _write_m3u(paths, output_dir, "energy_mix")


# ── orchestrator ──────────────────────────────────────────────────────────────

def generate_all(
    matched: list[MatchResult],
    unmatched: list[HistoryEntry],
    library: list[LibraryTrack],
    history: list[HistoryEntry],
    size: int,
    rediscovery_days: int,
    output_dir: str,
) -> list[str]:
    pl_dir = Path(output_dir) / "playlists"
    written: list[str] = []

    generators = [
        lambda: generate_listen_again(matched, history, size, pl_dir),
        lambda: generate_favorites(matched, history, size, pl_dir),
        lambda: generate_rediscovery(matched, history, size, rediscovery_days, pl_dir),
        lambda: generate_fresh_rotation(matched, library, size, pl_dir),
        lambda: generate_energy_mix(matched, library, history, size, pl_dir),
    ]

    for gen in generators:
        try:
            p = gen()
            written.append(str(p))
        except Exception as exc:
            logger.warning("Playlist generator failed: %s", exc)

    return written
