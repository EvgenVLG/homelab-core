from difflib import SequenceMatcher
from collections import defaultdict
from types import SimpleNamespace
import csv
import os
import re

import app.ingest as ingest
import app.library_scan as library_scan

INPUT_DIR = "/data/input"
LIBRARY_DIR = "/data/library"

OUTPUT_DIR = "/data/output"
MATCHED_OUT = os.path.join(OUTPUT_DIR, "baseline_matched_tracks.csv")
UNMATCHED_OUT = os.path.join(OUTPUT_DIR, "baseline_unmatched_history.csv")
SUMMARY_OUT = os.path.join(OUTPUT_DIR, "baseline_summary.txt")


def norm(s):
    return " ".join(str(s or "").strip().lower().split())


def title_norm(s):
    s = str(s or "").lower().strip()

    replacements = {
        "’": "'",
        "‘": "'",
        "`": "'",
        "“": '"',
        "”": '"',
        "&": "and",
    }
    for a, b in replacements.items():
        s = s.replace(a, b)

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


def seq_ratio(a, b):
    return SequenceMatcher(None, title_norm(a), title_norm(b)).ratio()


def token_set(s):
    return set(title_norm(s).split())


def token_overlap(a, b):
    ta = token_set(a)
    tb = token_set(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def to_obj(x):
    if isinstance(x, dict):
        return SimpleNamespace(**x)
    return x


def get_attr(x, name, default=""):
    v = getattr(x, name, default)
    return "" if v is None else v


def get_title(x):
    return getattr(x, "title", None) or getattr(x, "track", "")


def title_score(a, b):
    an = title_norm(a)
    bn = title_norm(b)

    if not an or not bn:
        return 0.0

    if an == bn:
        return 1.0

    if an in bn or bn in an:
        return 0.92

    sr = seq_ratio(a, b)
    to = token_overlap(a, b)

    # short-title guard: do not let "Paul" match "Slim Shady" nonsense
    if len(an) <= 8 or len(bn) <= 8:
        return max(sr * 0.55, to)

    return max(sr * 0.65 + to * 0.35, to)


def score_track(h, l):
    artist_ratio = 1.0 if norm(get_attr(h, "artist")) == norm(get_attr(l, "artist")) else 0.0
    tr = title_score(get_title(h), get_attr(l, "title"))
    score = 0.55 * artist_ratio + 0.45 * tr
    return score, artist_ratio, tr


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    history = ingest.ingest(INPUT_DIR)
    library = [to_obj(x) for x in library_scan.scan_library(LIBRARY_DIR)]

    artist_index = defaultdict(list)
    for l in library:
        artist_index[norm(get_attr(l, "artist"))].append(l)

    matched_rows = []
    unmatched_rows = []

    for h in history:
        candidates = artist_index.get(norm(get_attr(h, "artist")), [])

        best = None
        best_score = 0.0
        best_ar = 0.0
        best_tr = 0.0

        for l in candidates:
            score, ar, tr = score_track(h, l)
            if score > best_score:
                best_score = score
                best = l
                best_ar = ar
                best_tr = tr

        if best and best_ar >= 0.95 and best_tr >= 0.72 and best_score >= 0.82:
            matched_rows.append({
                "history_artist": get_attr(h, "artist"),
                "history_track": get_title(h),
                "library_artist": get_attr(best, "artist"),
                "library_title": get_attr(best, "title"),
                "score": round(best_score, 4),
                "artist_ratio": round(best_ar, 4),
                "title_ratio": round(best_tr, 4),
            })
        else:
            unmatched_rows.append({
                "history_artist": get_attr(h, "artist"),
                "history_track": get_title(h),
                "best_score": round(best_score, 4) if best else "",
            })

    with open(MATCHED_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "history_artist", "history_track",
            "library_artist", "library_title",
            "score", "artist_ratio", "title_ratio"
        ])
        w.writeheader()
        w.writerows(matched_rows)

    with open(UNMATCHED_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "history_artist", "history_track", "best_score"
        ])
        w.writeheader()
        w.writerows(unmatched_rows)

    total = len(history)
    matched = len(matched_rows)
    unmatched = len(unmatched_rows)
    rate = matched / total * 100 if total else 0.0

    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        f.write(f"history={total}\n")
        f.write(f"matched={matched}\n")
        f.write(f"unmatched={unmatched}\n")
        f.write(f"match_rate={rate:.2f}\n")

    print(f"history: {total}")
    print(f"library: {len(library)}")
    print(f"matched={matched} unmatched={unmatched} rate={rate:.2f}%")


if __name__ == "__main__":
    main()
