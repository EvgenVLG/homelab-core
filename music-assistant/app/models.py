"""
Core data models. Plain dataclasses — no ORM, no magic.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class HistoryEntry:
    source: str       # "youtube_music_json", "csv", etc.
    artist: str
    track: str
    album: str = ""
    timestamp: str = ""   # ISO string or raw; empty if unavailable
    play_count: int = 1   # some exports include a count
    raw_text: str = ""    # original line, kept for debugging


@dataclass
class LibraryTrack:
    path: str         # absolute path to audio file
    filename: str     # basename without extension
    artist: str       # inferred from directory structure or tag
    album: str        # inferred from directory structure or tag
    title: str        # inferred from filename or tag
    extension: str


@dataclass
class MatchResult:
    history_artist: str
    history_track: str
    library_path: str
    library_artist: str
    library_title: str
    score: float      # 0.0–1.0
    reason: str       # human-readable match explanation


@dataclass
class Stats:
    history_entries: int = 0
    unique_history_tracks: int = 0
    library_tracks: int = 0
    matched: int = 0
    unmatched: int = 0
    playlists_generated: list[str] = field(default_factory=list)
