import csv
from collections import defaultdict
from pathlib import Path


def _field(obj, name, default=""):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def build_missing_tracks(unmatched):
    grouped = {}

    for row in unmatched:
        artist = (_field(row, "artist", "") or "").strip()
        title = (_field(row, "title", "") or "").strip()
        album = (_field(row, "album", "") or "").strip()
        played_at = _field(row, "played_at", "")

        key = (artist.lower(), title.lower())

        if key not in grouped:
            grouped[key] = {
                "artist": artist,
                "title": title,
                "album_hint": album,
                "play_count": 0,
                "first_seen": played_at or "",
                "last_seen": played_at or "",
            }

        grouped[key]["play_count"] += 1

        if played_at:
            if not grouped[key]["first_seen"] or played_at < grouped[key]["first_seen"]:
                grouped[key]["first_seen"] = played_at
            if not grouped[key]["last_seen"] or played_at > grouped[key]["last_seen"]:
                grouped[key]["last_seen"] = played_at

    rows = []
    for item in grouped.values():
        play_count = item["play_count"]
        priority = float(play_count)

        rows.append({
            "artist": item["artist"],
            "title": item["title"],
            "album_hint": item["album_hint"],
            "play_count": play_count,
            "priority": round(priority, 2),
            "first_seen": item["first_seen"],
            "last_seen": item["last_seen"],
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
        "missing_summary_csv": str(summary_csv),
        "missing_tracks_count": len(missing_tracks),
        "missing_artist_album_groups": len(missing_summary),
    }
