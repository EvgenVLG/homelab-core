from difflib import SequenceMatcher
from collections import defaultdict
from types import SimpleNamespace
import csv
import os

import app.ingest as ingest
import app.library_scan as library_scan


INPUT_DIR = "/data/input"
LIBRARY_DIR = "/data/library"

OUTPUT_DIR = "/data/output"
MATCHED_OUT = os.path.join(OUTPUT_DIR, "baseline_matched_tracks.csv")
UNMATCHED_OUT = os.path.join(OUTPUT_DIR, "baseline_unmatched_history.csv")
SUMMARY_OUT = os.path.join(OUTPUT_DIR, "baseline_summary.txt")


def norm(s):
    if s is None:
        return ""
    return str(s).strip().lower()


def ratio(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def to_obj(x):
    if isinstance(x, dict):
        return SimpleNamespace(**x)
    return x


def get_attr(x, name, default=""):
    v = getattr(x, name, default)
    return "" if v is None else v


def get_title(x):
    # 🔥 ключевой фикс
    return getattr(x, "title", None) or getattr(x, "track", "")


def build_artist_index(library_tracks):
    idx = defaultdict(list)
    for t in library_tracks:
        artist = norm(get_attr(t, "artist"))
        if artist:
            idx[artist].append(t)
    return idx


def score_track(h, l):
    h_artist = get_attr(h, "artist")
    h_title = get_title(h)
    h_album = get_attr(h, "album")

    l_artist = get_attr(l, "artist")
    l_title = get_attr(l, "title")
    l_album = get_attr(l, "album")

    artist_exact = norm(h_artist) == norm(l_artist)
    artist_ratio = ratio(h_artist, l_artist)
    title_ratio = ratio(h_title, l_title)

    score = 0.0
    if artist_exact:
        score += 0.6
    else:
        score += 0.3 * artist_ratio

    score += 0.4 * title_ratio

    return score


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    history_tracks = ingest.ingest(INPUT_DIR)
    library_tracks = [to_obj(x) for x in library_scan.scan_library(LIBRARY_DIR)]

    print("history:", len(history_tracks))
    print("library:", len(library_tracks))

    artist_index = build_artist_index(library_tracks)

    matched = 0
    unmatched = 0

    for h in history_tracks:
        h_artist = norm(get_attr(h, "artist"))
        candidates = artist_index.get(h_artist, [])

        best_score = 0

        for l in candidates:
            s = score_track(h, l)
            if s > best_score:
                best_score = s

        if best_score >= 0.6:
            matched += 1
        else:
            unmatched += 1

    total = len(history_tracks)
    rate = (matched / total * 100) if total else 0

    with open(SUMMARY_OUT, "w") as f:
        f.write(f"history={total}\n")
        f.write(f"matched={matched}\n")
        f.write(f"unmatched={unmatched}\n")
        f.write(f"match_rate={rate:.2f}\n")

    print(f"matched={matched} unmatched={unmatched} rate={rate:.2f}%")


if __name__ == "__main__":
    main()
