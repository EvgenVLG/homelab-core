from difflib import SequenceMatcher
import inspect

import app.ingest as ingest
import app.library_scan as library_scan
import app.match_engine as me


def norm(s):
    if s is None:
        return ""
    return str(s).strip().lower()


def ratio(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def load_first(mod, names):
    for name in names:
        fn = getattr(mod, name, None)
        if callable(fn):
            try:
                data = fn()
                return data, name
            except Exception as e:
                print(f"FAILED {mod.__name__}.{name}(): {e}")
    return None, None


history_tracks, h_name = load_first(ingest, [
    "load_history", "ingest_history", "read_history", "get_history_tracks", "run_ingest"
])
library_tracks, l_name = load_first(library_scan, [
    "scan_library", "load_library", "get_library_tracks", "run_scan"
])

print("history loader:", h_name)
print("library loader:", l_name)
print("history count:", len(history_tracks) if history_tracks else 0)
print("library count:", len(library_tracks) if library_tracks else 0)

if not history_tracks or not library_tracks:
    raise SystemExit("Could not load tracks")

print("\n=== HISTORY SAMPLE ===")
for i, h in enumerate(history_tracks[:10], 1):
    print(f"[{i}] artist={getattr(h,'artist',None)!r} title={getattr(h,'title',None)!r} album={getattr(h,'album',None)!r}")

print("\n=== LIBRARY SAMPLE ===")
for i, l in enumerate(library_tracks[:10], 1):
    print(f"[{i}] artist={getattr(l,'artist',None)!r} title={getattr(l,'title',None)!r} album={getattr(l,'album',None)!r} path={getattr(l,'path',None)!r}")

print("\n=== CANDIDATE PROBE ===")
for h in history_tracks[:20]:
    h_artist = getattr(h, "artist", "")
    h_title = getattr(h, "title", "")
    candidates = [l for l in library_tracks if norm(getattr(l, "artist", "")) == norm(h_artist)]
    print(f"\nHISTORY: {h_artist!r} - {h_title!r}")
    print("artist-exact candidates:", len(candidates))

    ranked = sorted(
        (
            (
                ratio(h_title, getattr(l, "title", "")),
                getattr(l, "artist", None),
                getattr(l, "title", None),
                getattr(l, "album", None),
                getattr(l, "path", None),
            )
            for l in candidates
        ),
        reverse=True,
    )[:5]

    for score, artist, title, album, path in ranked:
        print(f"  score={score:.4f} | {artist!r} | {title!r} | {album!r} | {path!r}")

print("\n=== MATCH ENGINE CALLABLES ===")
for name in dir(me):
    if name.startswith("_"):
        continue
    obj = getattr(me, name)
    if callable(obj):
        try:
            sig = inspect.signature(obj)
        except Exception:
            sig = "(signature unavailable)"
        print(f"{name}{sig}")
