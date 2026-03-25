from collections import defaultdict
from pathlib import Path
import csv


def _field(obj, name, default=""):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _history_title(row):
    return (_field(row, "title", "") or _field(row, "track", "") or "").strip()


def _variant_type(title: str) -> str:
    t = (title or "").lower()

    if "karaoke" in t:
        return "karaoke"
    if "8d" in t:
        return "8d"
    if "slowed" in t or "reverb" in t or "sped up" in t or "speed up" in t:
        return "edit"
    if "nightcore" in t:
        return "nightcore"
    if "tutorial" in t or "reaction" in t:
        return "noise"
    if "lyrics video" in t or "official video" in t:
        return "video"
    if "cover" in t:
        return "cover"
    if "rock version" in t:
        return "rock_version"
    if "acoustic" in t:
        return "acoustic"
    if "unplugged" in t:
        return "unplugged"
    if "live" in t:
        return "live"
    if "instrumental" in t:
        return "instrumental"
    if "video edit" in t:
        return "edit"
    if "edit" in t:
        return "edit"
    if "remix" in t:
        return "remix"
    return "standard"


def build_missing_tracks(unmatched):
    grouped = {}

    for row in unmatched:
        artist = (_field(row, "artist", "") or "").strip()
        title = _history_title(row)
        album_hint = (_field(row, "album", "") or "").strip()
        play_count = int(_field(row, "play_count", 1) or 1)
        first_seen = (_field(row, "timestamp", "") or "").strip()
        last_seen = (_field(row, "timestamp", "") or "").strip()

        if not artist and not title:
            continue
        if not title:
            continue

        key = (artist.lower(), title.lower())

        if key not in grouped:
            grouped[key] = {
                "artist": artist,
                "title": title,
                "album_hint": album_hint,
                "play_count": 0,
                "priority": 0.0,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "variant_type": _variant_type(title),
            }

        grouped[key]["play_count"] += play_count

        if first_seen:
            if not grouped[key]["first_seen"] or first_seen < grouped[key]["first_seen"]:
                grouped[key]["first_seen"] = first_seen

        if last_seen:
            if not grouped[key]["last_seen"] or last_seen > grouped[key]["last_seen"]:
                grouped[key]["last_seen"] = last_seen

    rows = []
    for item in grouped.values():
        item["priority"] = float(item["play_count"])
        rows.append({
            "artist": item["artist"],
            "title": item["title"],
            "album_hint": item["album_hint"],
            "play_count": item["play_count"],
            "priority": item["priority"],
            "first_seen": item["first_seen"],
            "last_seen": item["last_seen"],
            "variant_type": item["variant_type"],
            "search_query": f'{item["artist"]} - {item["title"]}'.strip(" -"),
        })

    rows.sort(key=lambda x: (-x["priority"], -x["play_count"], x["artist"], x["title"]))
    return rows


def build_missing_artist_album_summary(missing_tracks):
    grouped = defaultdict(lambda: {
        "artist": "",
        "album_hint": "",
        "missing_tracks": 0,
        "total_plays": 0,
        "top_titles": [],
    })

    for row in missing_tracks:
        artist = row["artist"]
        album_hint = row["album_hint"]
        key = (artist.lower(), album_hint.lower())

        grouped[key]["artist"] = artist
        grouped[key]["album_hint"] = album_hint
        grouped[key]["missing_tracks"] += 1
        grouped[key]["total_plays"] += int(row["play_count"])
        grouped[key]["top_titles"].append((row["title"], int(row["play_count"])))

    summary = []
    for item in grouped.values():
        top_titles = sorted(item["top_titles"], key=lambda x: -x[1])[:5]
        summary.append({
            "artist": item["artist"],
            "album_hint": item["album_hint"],
            "missing_tracks": item["missing_tracks"],
            "total_plays": item["total_plays"],
            "top_titles": "; ".join(title for title, _ in top_titles),
        })

    summary.sort(key=lambda x: (-x["total_plays"], -x["missing_tracks"], x["artist"]))
    return summary


def write_missing_queue(unmatched, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    missing_tracks = build_missing_tracks(unmatched)
    missing_summary = build_missing_artist_album_summary(missing_tracks)

    tracks_csv = output_dir / "missing_tracks.csv"
    summary_csv = output_dir / "missing_artists_albums.csv"

    with tracks_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "artist",
                "title",
                "album_hint",
                "play_count",
                "priority",
                "first_seen",
                "last_seen",
                "variant_type",
                "search_query",
            ],
        )
        writer.writeheader()
        writer.writerows(missing_tracks)

    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "artist",
                "album_hint",
                "missing_tracks",
                "total_plays",
                "top_titles",
            ],
        )
        writer.writeheader()
        writer.writerows(missing_summary)

    return {
        "missing_tracks_csv": str(tracks_csv),
        "missing_artists_albums_csv": str(summary_csv),
        "missing_tracks_count": len(missing_tracks),
        "missing_artist_album_groups": len(missing_summary),
    }
