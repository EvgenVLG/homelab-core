import logging
import re
from pathlib import Path
from types import SimpleNamespace

log = logging.getLogger(__name__)

AUDIO_EXTENSIONS_DEFAULT = (".mp3", ".flac", ".m4a", ".aac", ".ogg", ".wav")


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _strip_extension(name: str) -> str:
    return Path(name).stem


def _clean_artist(text: str) -> str:
    text = (text or "").replace("_", " ").strip()
    return _normalize_whitespace(text)


def _normalize_compare(text: str) -> str:
    text = (text or "").lower().replace("_", " ").strip()
    text = re.sub(r"\(\d{4}\)", "", text)
    text = re.sub(r"\[\d{4}\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_title(raw_title: str, artist: str | None = None, album: str | None = None) -> str:
    text = _strip_extension(raw_title)
    text = text.replace("_", " ").strip()

    for _ in range(3):
        new_text = re.sub(r"^\s*\d{1,2}\s*[-._)\]]\s*", "", text)
        if new_text == text:
            new_text = re.sub(r"^\s*\d{1,2}\s+", "", text)
        if new_text == text:
            break
        text = new_text.strip()

    parts = [p.strip() for p in re.split(r"\s+-\s+", text) if p.strip()]

    artist_l = _normalize_compare(artist or "")
    album_l = _normalize_compare(album or "")

    changed = True
    while changed and len(parts) > 1:
        changed = False
        head = _normalize_compare(parts[0])

        if artist_l and head == artist_l:
            parts.pop(0)
            changed = True
            continue

        if album_l and head == album_l:
            parts.pop(0)
            changed = True
            continue

        if re.fullmatch(r"\d{1,2}", head):
            parts.pop(0)
            changed = True
            continue

        if re.fullmatch(r"(cd|disc)\s*\d+", head):
            parts.pop(0)
            changed = True
            continue

    if parts and re.fullmatch(r"\d{1,2}", _normalize_compare(parts[0])):
        parts.pop(0)

    text = " - ".join(parts) if parts else text

    text = re.sub(r"\s*\[(official|lyrics?|audio|video|hd|hq)\]\s*$", "", text, flags=re.I)
    text = re.sub(r"\s*\((official|lyrics?|audio|video|hd|hq)\)\s*$", "", text, flags=re.I)

    return _normalize_whitespace(text)


def _derive_track_fields(path: Path) -> tuple[str | None, str]:
    stem = path.stem.replace("_", " ").strip()
    parts = [p.strip() for p in re.split(r"\s+-\s+", stem) if p.strip()]

    if len(parts) == 2:
        return parts[0], parts[1]

    return None, stem


def scan_library(library_dir, audio_extensions=AUDIO_EXTENSIONS_DEFAULT):
    tracks = []
    exts = {ext.lower() for ext in audio_extensions}

    for path in Path(library_dir).rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue

        tag_artist = None
        tag_title = None
        tag_album = None

        file_artist, file_title = _derive_track_fields(path)

        parent = path.parent.name if path.parent else ""
        grandparent = path.parent.parent.name if len(path.parts) >= 2 else ""

        album = tag_album or parent or ""
        artist = tag_artist or grandparent or file_artist or parent or ""
        raw_title = tag_title or file_title or path.stem
        clean_title = _clean_title(raw_title, artist=artist, album=album)

        tracks.append(SimpleNamespace(
            path=str(path),
            artist=_clean_artist(artist),
            title=clean_title,
            album=_normalize_whitespace(album),
            extension=path.suffix.lower(),
        ))

    log.info("Library scan complete: %s tracks found in %s", len(tracks), library_dir)
    return tracks
