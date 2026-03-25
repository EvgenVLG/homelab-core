from app.config import load_config
from app.ingest import ingest
from app.library_scan import scan_library
from app.match_engine import match
from app.missing_queue import write_missing_queue


def main():
    cfg = load_config()

    print("[missing] ingest...")
    history = ingest(cfg.input_dir)

    print("[missing] scan library...")
    library = scan_library(cfg.library_dir, cfg.audio_extensions)

    print("[missing] match...")
    matched, unmatched = match(history, library, cfg.match_threshold)

    print("[missing] build queue...")
    result = write_missing_queue(unmatched, cfg.output_dir)

    print("\nMissing queue built:")
    for k, v in result.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
