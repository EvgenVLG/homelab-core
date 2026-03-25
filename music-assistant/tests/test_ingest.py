import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.ingest import ingest


def _write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


class TestIngestJSON(unittest.TestCase):

    def test_generic_json(self):
        with tempfile.TemporaryDirectory() as d:
            data = [
                {"artist": "Radiohead", "track": "Creep", "play_count": 5},
                {"artist": "Nirvana",   "title": "Smells Like Teen Spirit"},
            ]
            _write(Path(d), "history.json", json.dumps(data))
            entries = ingest(d)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].artist, "Radiohead")
        self.assertEqual(entries[0].play_count, 5)
        self.assertEqual(entries[1].track, "Smells Like Teen Spirit")

    def test_google_takeout_json(self):
        with tempfile.TemporaryDirectory() as d:
            data = [{
                "header": "YouTube Music",
                "title": "Watched Creep",
                "subtitles": [{"name": "Radiohead", "url": ""}],
                "time": "2024-01-15T10:30:00.000Z",
            }]
            _write(Path(d), "watch-history.json", json.dumps(data))
            entries = ingest(d)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].artist, "Radiohead")
        self.assertEqual(entries[0].track, "Creep")
        self.assertEqual(entries[0].source, "google_takeout")

    def test_google_takeout_strips_watched_prefix(self):
        with tempfile.TemporaryDirectory() as d:
            data = [{
                "header": "YouTube Music",
                "title": "Watched Karma Police",
                "subtitles": [{"name": "Radiohead", "url": ""}],
                "time": "",
            }]
            _write(Path(d), "history.json", json.dumps(data))
            entries = ingest(d)
        self.assertEqual(entries[0].track, "Karma Police")


class TestIngestCSV(unittest.TestCase):

    def test_csv_basic(self):
        with tempfile.TemporaryDirectory() as d:
            rows = "artist,track,album,play_count\nRadiohead,Creep,Pablo Honey,7\n"
            _write(Path(d), "history.csv", rows)
            entries = ingest(d)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].artist, "Radiohead")
        self.assertEqual(entries[0].play_count, 7)
        self.assertEqual(entries[0].album, "Pablo Honey")

    def test_csv_alternate_column_names(self):
        with tempfile.TemporaryDirectory() as d:
            rows = "Artist,Title\nNirvana,Lithium\n"
            _write(Path(d), "history.csv", rows)
            entries = ingest(d)
        self.assertEqual(entries[0].artist, "Nirvana")
        self.assertEqual(entries[0].track, "Lithium")

    def test_csv_multiple_rows(self):
        with tempfile.TemporaryDirectory() as d:
            rows = "artist,track\nA,X\nB,Y\nC,Z\n"
            _write(Path(d), "history.csv", rows)
            entries = ingest(d)
        self.assertEqual(len(entries), 3)


class TestIngestResilience(unittest.TestCase):

    def test_malformed_json_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "bad.json", "not json {{{{")
            _write(Path(d), "good.json",
                   json.dumps([{"artist": "OK", "track": "Fine"}]))
            entries = ingest(d)
        self.assertEqual(len(entries), 1)

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as d:
            entries = ingest(d)
        self.assertEqual(entries, [])

    def test_unsupported_extension_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "history.txt", "artist,track\nFoo,Bar\n")
            entries = ingest(d)
        self.assertEqual(entries, [])

    def test_missing_directory(self):
        entries = ingest("/tmp/does_not_exist_abc123")
        self.assertEqual(entries, [])

    def test_mixed_valid_and_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "bad.json",  "{{invalid}}")
            _write(Path(d), "good.csv",  "artist,track\nA,B\n")
            entries = ingest(d)
        self.assertEqual(len(entries), 1)


if __name__ == "__main__":
    unittest.main()
