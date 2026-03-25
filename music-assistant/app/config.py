"""
Config from environment variables with safe defaults.
All paths default to Docker mount points.
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    input_dir: str
    library_dir: str
    output_dir: str
    playlist_size: int
    match_threshold: float
    audio_extensions: frozenset[str]
    rediscovery_days: int   # tracks not played in this many days qualify
    log_level: str


def load_config() -> Config:
    def _path(key: str, default: str) -> str:
        return os.environ.get(key, default).rstrip("/")

    return Config(
        input_dir=_path("INPUT_DIR", "/data/input"),
        library_dir=_path("LIBRARY_DIR", "/data/library"),
        output_dir=_path("OUTPUT_DIR", "/data/output"),
        playlist_size=int(os.environ.get("PLAYLIST_SIZE", "30")),
        match_threshold=float(os.environ.get("MATCH_THRESHOLD", "0.6")),
        audio_extensions=frozenset(
            os.environ.get(
                "AUDIO_EXTENSIONS",
                ".mp3,.flac,.ogg,.m4a,.aac,.opus,.wav,.wma,.aiff",
            ).split(",")
        ),
        rediscovery_days=int(os.environ.get("REDISCOVERY_DAYS", "90")),
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    )
