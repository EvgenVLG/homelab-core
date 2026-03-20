"""Single call to configure logging for the entire app."""
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=numeric,
        format=fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
