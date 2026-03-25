import logging
import re
from collections import defaultdict
from difflib import SequenceMatcher
from types import SimpleNamespace

log = logging.getLogger(__name__)


def _norm(s):
    return " ".join(str(s or "").lower().strip().split())


def _title_norm(s):
    s = str(s or "").lower().strip()

    s = s.replace("’", "'").replace("‘", "'")

    s = re.sub(r"\bfeat\.?\b.*$", "", s)
    s = re.sub(r"\bft\.?\b.*$", "", s)
    s = re.sub(r"\(.*?version.*?\)", "", s)
    s = re.sub(r"\(edit\)", "", s)
    s = re.sub(r"\(mix\)", "", s)
    s = re.sub(r"\(remaster.*?\)", "", s)
    s = re.sub(r"\(.*?live.*?\)", "", s)
    s = re.sub(r"\[.*?\]", "", s)

    s = re.sub(r"[^a-z0-9а-яё\s']", " ", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _seq_ratio(a, b):
    return SequenceMatcher(None, _title_norm(a), _title_norm(b)).ratio()


def _tokens(s):
    return set(_title_norm(s).split())


def _token_overlap(a, b):
    ta = _tokens(a)
    tb = _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _field(obj, name, default=""):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _to_obj(obj):
    if isinstance(obj, dict):
        return SimpleNamespace(**obj)
    return obj


def _title_score(a, b):
    an = _title_norm(a)
    bn = _title_norm(b)

    if not an or not bn:
        return 0.0

    if an == bn:
        return 1.0

    if an in bn or bn in an:
        return 0.92

    sr = _seq_ratio(a, b)
    to = _token_overlap(a, b)

    # short title protection
    if len(an) <= 8 or len(bn) <= 8:
        return max(sr * 0.55, to)

    return max(sr * 0.65 + to * 0.35, to)


def _score(h, l):
    h_artist = _norm(_field(h, "artist"))
    l_artist = _norm(_field(l, "artist"))

    artist_exact = h_artist == l_artist
    artist_score = 1.0 if artist_exact else 0.0

    tr = _title_score(_field(h, "title") or _field(h, "track"), _field(l, "title"))

    score = 0.55 * artist_score + 0.45 * tr

    return {
        "score": score,
        "artist_score": artist_score,
        "title_ratio": tr,
        "track_token_score": tr,  # compatibility stub
    }


def _accept(info):
    return (
        info["artist_score"] >= 0.95 and
        info["title_ratio"] >= 0.72 and
        info["score"] >= 0.82
    )


def match(history_entries, library_tracks, threshold=0.60):
    by_artist = defaultdict(list)

    for t in library_tracks:
        by_artist[_norm(_field(t, "artist"))].append(t)

    matched = []
    unmatched = []

    for h in history_entries:
        candidates = by_artist.get(_norm(_field(h, "artist")), [])

        best = None
        best_info = None

        for l in candidates:
            info = _score(h, l)
            if best_info is None or info["score"] > best_info["score"]:
                best = l
                best_info = info

        if best and best_info and _accept(best_info):
            matched.append(SimpleNamespace(
                history_artist=_field(h, "artist"),
                history_track=_field(h, "track") or _field(h, "title"),
                library_path=_field(best, "path"),
                library_artist=_field(best, "artist"),
                library_title=_field(best, "title"),
                score=round(best_info["score"], 4),
                reason=f"title={best_info['title_ratio']:.2f}"
            ))
        else:
            unmatched.append(_to_obj(h))

    log.info("match: %s matched / %s unmatched", len(matched), len(unmatched))

    return matched, unmatched
