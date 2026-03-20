"""
Recursively scan a local music library directory.

Path convention assumed (most common self-hosted layouts):
  <library_root>/<Artist>/<Album>/<track>.<ext>
  <library_root>/<Artist>/<track>.<ext>

Tags are read via mutagen if installed; otherwise falls back to
path-based inference. The scanner works without mutagen — it just
produces slightly less accurate metadata for non-standard layouts.
"""
from __future__ import annotations
import logging
import os
import re
from pathlib import Path

from .models import LibraryTrack

logger = logging.getLogger(__name__)

try:
    import mutagen  # type: ignore
    _MUTAGEN = True
    logger.debug("mutagen available — tag reading enabled")
except ImportError:
    _MUTAGEN = False
    logger.debug("mutagen not installed — using path-based metadata inference only")


# Strip common numeric track prefixes: "01 - ", "02. ", "3 "
_TRACKNUM_RE = re.compile(r"^\d{1,3}[\s.\-_]+")


def _read_tags(path: Path) -> tuple[str, str, str]:
    """Return (artist, album, title) from file tags. Returns empty strings on failure."""
    if not _MUTAGEN:
        return "", "", ""
    try:
        f = mutagen.File(path, easy=True)
        if f is None:
            return "", "", ""

        def _first(key: str) -> str:
            val = f.get(key)
            return str(val[0]).strip() if val else ""

        return _first("artist"), _first("album"), _first("title")
    except Exception as exc:
        logger.debug("Tag read failed for %s: %s", path.name, exc)
        return "", "", ""


def _infer_from_path(path: Path, library_root: Path) -> tuple[str, str, str]:
    """
    Infer (artist, album, title) from path segments relative to library root.

    depth ≥ 3:  parts[-3] = artist, parts[-2] = album, parts[-1] = file
    depth == 2: parts[-2] = artist, parts[-1] = file
    depth == 1: no artist/album, only title from filename
    """
    try:
        rel = path.relative_to(library_root)
    except ValueError:
        rel = path

    parts = list(rel.parts)
    stem = _TRACKNUM_RE.sub("", path.stem).strip()

    if len(parts) >= 3:
        return parts[-3], parts[-2], stem
    elif len(parts) == 2:
        return parts[-2], "", stem
    else:
        return "", "", stem


def scan_library(library_dir: str, audio_extensions: frozenset[str]) -> list[LibraryTrack]:
    """Walk library_dir and return a LibraryTrack for every audio file found."""
    tracks: list[LibraryTrack] = []
    root = Path(library_dir)

    if not root.exists():
        logger.error("Library directory does not exist: %s", library_dir)
        return tracks

    for dirpath, _dirs, filenames in os.walk(root):
        for name in sorted(filenames):
            ext = Path(name).suffix.lower()
            if ext not in audio_extensions:
                continue

            abs_path = Path(dirpath) / name
            tag_artist, tag_album, tag_title = _read_tags(abs_path)
            inf_artist, inf_album, inf_title = _infer_from_path(abs_path, root)

            tracks.append(
                LibraryTrack(
                    path=str(abs_path),
                    filename=Path(name).stem,
                    artist=tag_artist or inf_artist,
                    album=tag_album or inf_album,
                    title=tag_title or inf_title,
                    extension=ext,
                )
            )

    logger.info("Library scan complete: %d tracks found in %s", len(tracks), library_dir)
    return tracks
