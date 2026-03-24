import logging
import re
from collections import defaultdict
from difflib import SequenceMatcher
from types import SimpleNamespace

log = logging.getLogger(__name__)


def _norm(text: str) -> str:
    text = (text or "").lower().strip()
    text = text.replace("&", " and ")
    text = re.sub(r"[\(\)\[\]\{\}]", " ", text)
    text = re.sub(r"[^a-z0-9а-яё\s\-]", " ", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokens(text: str) -> set[str]:
    stop = {"the", "a", "an", "and", "feat", "ft", "featuring"}
    return {t for t in _norm(text).split() if t and t not in stop}


def _sequence_ratio(a: str, b: str) -> float:
    a = _norm(a)
    b = _norm(b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _token_overlap(a: str, b: str) -> float:
    ta = _tokens(a)
    tb = _tokens(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    return inter / max(len(ta), len(tb))


def _field(obj, name: str, default=""):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _to_dict(obj):
    if isinstance(obj, dict):
        return dict(obj)

    data = {}
    # grab public attributes from objects / dataclasses / namespaces
    if hasattr(obj, "__dict__"):
        for k, v in vars(obj).items():
            if not k.startswith("_"):
                data[k] = v

    # fill common fields if missing
    for key in (
        "artist",
        "title",
        "album",
        "path",
        "extension",
        "played_at",
        "count",
        "score",
        "reason",
        "library_path",
        "library_artist",
        "library_title",
        "artist_score",
        "title_ratio",
        "track_token_score",
    ):
        if key not in data and hasattr(obj, key):
            data[key] = getattr(obj, key)

    return data


def _to_obj(obj):
    if isinstance(obj, dict):
        return SimpleNamespace(**obj)
    return obj


def _artist_score(history_artist: str, library_artist: str) -> float:
    return max(
        _sequence_ratio(history_artist, library_artist),
        _token_overlap(history_artist, library_artist),
    )


def _score(history_entry, library_track) -> dict:
    h_artist = _field(history_entry, "artist", "") or ""
    h_title = _field(history_entry, "title", "") or ""
    l_artist = _field(library_track, "artist", "") or ""
    l_title = _field(library_track, "title", "") or ""

    artist_score = _artist_score(h_artist, l_artist)
    title_ratio = _sequence_ratio(h_title, l_title)
    track_token_score = _token_overlap(h_title, l_title)

    total_score = (
        artist_score * 0.35 +
        title_ratio * 0.40 +
        track_token_score * 0.25
    )

    return {
        "score": total_score,
        "artist_score": artist_score,
        "title_ratio": title_ratio,
        "track_token_score": track_token_score,
    }


def _accept(score_info: dict, threshold: float) -> bool:
    score = score_info["score"]
    artist_score = score_info["artist_score"]
    title_ratio = score_info["title_ratio"]
    track_token_score = score_info["track_token_score"]

    if artist_score < 0.70:
        return False

    if title_ratio < 0.55 and track_token_score < 0.50:
        return False

    if artist_score >= 0.90 and title_ratio < 0.45 and track_token_score < 0.60:
        return False

    return score >= threshold


def match(history_entries, library_tracks, threshold=0.60):
    by_artist = defaultdict(list)

    for track in library_tracks:
        by_artist[_norm(_field(track, "artist", ""))].append(track)

    unique_history = []
    seen = set()

    for entry in history_entries:
        key = (
            _norm(_field(entry, "artist", "")),
            _norm(_field(entry, "title", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_history.append(entry)

    log.info(
        "Matching %s unique history entries against %s library tracks (threshold=%.2f)",
        len(unique_history),
        len(library_tracks),
        threshold,
    )

    matched = []
    unmatched = []

    for entry in unique_history:
        artist_key = _norm(_field(entry, "artist", ""))
        candidates = by_artist.get(artist_key, [])
        if not candidates:
            candidates = library_tracks

        best_track = None
        best_info = None

        for track in candidates:
            info = _score(entry, track)
            if best_info is None or info["score"] > best_info["score"]:
                best_track = track
                best_info = info

        if best_track and best_info and _accept(best_info, threshold):
            entry_data = _to_dict(entry)

            entry_data["library_path"] = _field(best_track, "path", "")
            entry_data["library_artist"] = _field(best_track, "artist", "")
            entry_data["library_title"] = _field(best_track, "title", "")
            entry_data["score"] = round(best_info["score"], 4)
            entry_data["artist_score"] = round(best_info["artist_score"], 4)
            entry_data["title_ratio"] = round(best_info["title_ratio"], 4)
            entry_data["track_token_score"] = round(best_info["track_token_score"], 4)
            entry_data["reason"] = (
                f"artist={best_info['artist_score']:.2f}; "
                f"title_ratio={best_info['title_ratio']:.2f}; "
                f"track_token={best_info['track_token_score']:.2f}"
            )

            matched.append(_to_obj(entry_data))
        else:
            unmatched.append(_to_obj(_to_dict(entry)))

    hit_rate = (len(matched) / len(unique_history) * 100.0) if unique_history else 0.0
    log.info(
        "Match complete: %s matched, %s unmatched (%.1f%% hit rate)",
        len(matched),
        len(unmatched),
        hit_rate,
    )

    return matched, unmatched
