import csv
from pathlib import Path
from types import SimpleNamespace

from app.config import load_config
from app.ingest import ingest
from app.library_scan import scan_library
from app.match_engine import match
from app.missing_queue import write_missing_queue


def main():
    cfg = load_config()
    history = ingest(cfg.input_dir)
    library = scan_library(cfg.library_dir, cfg.audio_extensions)
    matched, unmatched = match(history, library, cfg.match_threshold)

    result = write_missing_queue(unmatched, cfg.output_dir)

    print("Missing queue built:")
    for k, v in result.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
