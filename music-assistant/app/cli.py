"""
CLI entrypoint.

Commands:
  ingest              Parse input history files → print entry count
  scan-library        Walk library dir → print track count
  match               Match history to library tracks
  generate-playlists  Write .m3u playlist files
  stats               Print summary from existing output files
  run-all             Run the full pipeline end-to-end
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path

from .logging_setup import setup_logging
from .config import load_config

logger = logging.getLogger(__name__)


def cmd_ingest(cfg):
    from .ingest import ingest
    entries = ingest(cfg.input_dir)
    print(f"✓ Ingested {len(entries)} history entries from {cfg.input_dir}")
    return entries


def cmd_scan(cfg):
    from .library_scan import scan_library
    tracks = scan_library(cfg.library_dir, cfg.audio_extensions)
    print(f"✓ Found {len(tracks)} tracks in library")
    return tracks


def cmd_match(cfg, history=None, library=None):
    from .ingest import ingest
    from .library_scan import scan_library
    from .match_engine import match
    if history is None:
        history = ingest(cfg.input_dir)
    if library is None:
        library = scan_library(cfg.library_dir, cfg.audio_extensions)
    matched, unmatched = match(history, library, cfg.match_threshold)
    print(f"✓ Matched {len(matched)} / Unmatched {len(unmatched)}")
    return matched, unmatched, history, library


def cmd_generate(cfg, matched=None, unmatched=None, library=None, history=None):
    from .ingest import ingest
    from .library_scan import scan_library
    from .match_engine import match
    from .playlists import generate_all
    if matched is None:
        history = ingest(cfg.input_dir)
        library = scan_library(cfg.library_dir, cfg.audio_extensions)
        matched, unmatched = match(history, library, cfg.match_threshold)
    playlists = generate_all(
        matched, unmatched or [], library or [], history or [],
        cfg.playlist_size, cfg.rediscovery_days, cfg.output_dir,
    )
    print(f"✓ Generated {len(playlists)} playlists → {cfg.output_dir}/playlists/")
    return playlists


def cmd_stats(cfg):
    summary_path = Path(cfg.output_dir) / "summary.json"
    if not summary_path.exists():
        print("No summary.json found — run 'run-all' first.")
        return
    data = json.loads(summary_path.read_text())
    print("\n── Music Assistant Summary ─────────────────")
    for k, v in data.items():
        label = k.replace("_", " ")
        print(f"  {label:<30} {v}")
    print("────────────────────────────────────────────\n")


def cmd_run_all(cfg):
    from .ingest import ingest
    from .library_scan import scan_library
    from .match_engine import match
    from .playlists import generate_all
    from .stats import save_outputs

    print("── Step 1/4: Ingesting history ─────────────")
    history = ingest(cfg.input_dir)

    print("── Step 2/4: Scanning library ──────────────")
    library = scan_library(cfg.library_dir, cfg.audio_extensions)

    print("── Step 3/4: Matching ──────────────────────")
    matched, unmatched = match(history, library, cfg.match_threshold)

    print("── Step 4/4: Generating playlists ──────────")
    playlists = generate_all(
        matched, unmatched, library, history,
        cfg.playlist_size, cfg.rediscovery_days, cfg.output_dir,
    )

    stats = save_outputs(history, library, matched, unmatched, playlists, cfg.output_dir)

    match_rate = round(100 * stats.matched / max(stats.unique_history_tracks, 1), 1)
    print("\n── Run complete ────────────────────────────")
    print(f"  History entries  : {stats.history_entries}")
    print(f"  Unique tracks    : {stats.unique_history_tracks}")
    print(f"  Library tracks   : {stats.library_tracks}")
    print(f"  Matched          : {stats.matched}  ({match_rate}%)")
    print(f"  Unmatched        : {stats.unmatched}")
    print(f"  Playlists        : {', '.join(stats.playlists_generated) or 'none'}")
    print(f"  Output dir       : {cfg.output_dir}")
    print("────────────────────────────────────────────\n")


def main() -> None:
    setup_logging()
    cfg = load_config()

    parser = argparse.ArgumentParser(
        prog="music-assistant",
        description="Local music assistant — history → playlists",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ingest",              help="Parse input history files")
    sub.add_parser("scan-library",        help="Scan local music library")
    sub.add_parser("match",               help="Match history entries to library tracks")
    sub.add_parser("generate-playlists",  help="Write .m3u playlist files")
    sub.add_parser("stats",               help="Print summary statistics")
    sub.add_parser("run-all",             help="Run the full pipeline")

    args = parser.parse_args()
    dispatch = {
        "ingest":             lambda: cmd_ingest(cfg),
        "scan-library":       lambda: cmd_scan(cfg),
        "match":              lambda: cmd_match(cfg),
        "generate-playlists": lambda: cmd_generate(cfg),
        "stats":              lambda: cmd_stats(cfg),
        "run-all":            lambda: cmd_run_all(cfg),
    }
    dispatch[args.command]()


if __name__ == "__main__":
    main()
