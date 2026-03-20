"""
Match history entries against local library tracks.

Scoring model
─────────────
For each (history_entry, library_track) pair:
  artist_score  = token overlap between normalized artist strings    → 0–1
  title_ratio   = difflib SequenceMatcher ratio on normalized titles → 0–1
  title_tokens  = token overlap on track titles                       → 0–1
  track_score   = max(title_ratio, title_tokens)
  combined      = 0.45 * artist_score + 0.55 * track_score

If combined ≥ MATCH_THRESHOLD (default 0.6) → accepted.
Best candidate per history entry wins.

Deduplication
─────────────
History is first collapsed to unique (artist, track) pairs with
summed play_count so playlist ranking is meaningful.
"""
from __future__ import annotations
import logging
from difflib import SequenceMatcher

from .models import HistoryEntry, LibraryTrack, MatchResult
from .normalize import normalize, token_set

logger = logging.getLogger(__name__)


def _score(h: HistoryEntry, lib: LibraryTrack) -> tuple[float, str]:
    """Return (combined_score, reason_string) for a history/library pair."""
    h_tokens_artist = token_set(h.artist)
    l_tokens_artist = token_set(lib.artist)
    h_tokens_track = token_set(h.track)
    l_tokens_title = token_set(lib.title)

    # Artist: token overlap
    artist_union = len(h_tokens_artist | l_tokens_artist)
    artist_score = (
        len(h_tokens_artist & l_tokens_artist) / artist_union
        if artist_union else 0.0
    )

    # Track: sequence ratio + token overlap, take best
    h_track_n = normalize(h.track, remove_noise=True)
    l_title_n = normalize(lib.title, remove_noise=True)
    title_ratio = SequenceMatcher(None, h_track_n, l_title_n).ratio()

    track_union = len(h_tokens_track | l_tokens_title)
    track_token = (
        len(h_tokens_track & l_tokens_title) / track_union
        if track_union else 0.0
    )
    track_score = max(title_ratio, track_token)

    combined = round(0.45 * artist_score + 0.55 * track_score, 4)

    parts: list[str] = []
    if artist_score >= 0.4:
        parts.append(f"artist={artist_score:.2f}")
    if title_ratio >= 0.4:
        parts.append(f"title_ratio={title_ratio:.2f}")
    if track_token >= 0.4:
        parts.append(f"track_tokens={track_token:.2f}")

    return combined, ("; ".join(parts) or "below_threshold")


def _deduplicate_history(entries: list[HistoryEntry]) -> list[HistoryEntry]:
    """
    Merge duplicate (artist, track) pairs, summing play_count.
    Keeps the entry with the latest timestamp as the canonical record.
    """
    grouped: dict[tuple[str, str], HistoryEntry] = {}
    for e in entries:
        key = (normalize(e.artist), normalize(e.track))
        if key in grouped:
            existing = grouped[key]
            existing.play_count += e.play_count
            # Lexicographic comparison works correctly for ISO 8601 timestamps
            if e.timestamp > existing.timestamp:
                existing.timestamp = e.timestamp
        else:
            # Shallow copy so we can mutate play_count safely
            grouped[key] = HistoryEntry(
                source=e.source,
                artist=e.artist,
                track=e.track,
                album=e.album,
                timestamp=e.timestamp,
                play_count=e.play_count,
                raw_text=e.raw_text,
            )
    return list(grouped.values())


def match(
    history: list[HistoryEntry],
    library: list[LibraryTrack],
    threshold: float = 0.6,
) -> tuple[list[MatchResult], list[HistoryEntry]]:
    """
    Return (matched_results, unmatched_entries).

    For each unique history entry, find the best-scoring library track.
    Entries whose best score < threshold go to unmatched.
    """
    deduped = _deduplicate_history(history)
    logger.info(
        "Matching %d unique history entries against %d library tracks (threshold=%.2f)",
        len(deduped), len(library), threshold,
    )

    if not library:
        logger.warning("Library is empty — all history entries will be unmatched")
        return [], deduped

    matched: list[MatchResult] = []
    unmatched: list[HistoryEntry] = []

    for entry in deduped:
        best_score = 0.0
        best_track: LibraryTrack | None = None
        best_reason = ""

        for lib_track in library:
            score, reason = _score(entry, lib_track)
            if score > best_score:
                best_score = score
                best_track = lib_track
                best_reason = reason

        if best_score >= threshold and best_track is not None:
            matched.append(
                MatchResult(
                    history_artist=entry.artist,
                    history_track=entry.track,
                    library_path=best_track.path,
                    library_artist=best_track.artist,
                    library_title=best_track.title,
                    score=best_score,
                    reason=best_reason,
                )
            )
        else:
            unmatched.append(entry)

    logger.info(
        "Match complete: %d matched, %d unmatched (%.1f%% hit rate)",
        len(matched),
        len(unmatched),
        100 * len(matched) / max(len(deduped), 1),
    )
    return matched, unmatched
