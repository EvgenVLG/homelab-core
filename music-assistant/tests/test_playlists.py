import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.models import HistoryEntry, LibraryTrack, MatchResult
from app.playlists import (
    generate_listen_again,
    generate_favorites,
    generate_fresh_rotation,
    generate_rediscovery,
    generate_energy_mix,
    generate_all,
)


def _match(artist, track, path, score=0.9):
    return MatchResult(
        history_artist=artist, history_track=track,
        library_path=path, library_artist=artist,
        library_title=track, score=score, reason="test",
    )

def _entry(artist, track, plays=1, timestamp=""):
    return HistoryEntry(source="test", artist=artist, track=track,
                        play_count=plays, timestamp=timestamp)

def _lib(artist, title, path=None):
    return LibraryTrack(
        path=path or f"/lib/{artist}/{title}.mp3",
        filename=title, artist=artist, album="", title=title, extension=".mp3",
    )


MATCHED = [
    _match("Radiohead", "Creep",       "/lib/Radiohead/Creep.mp3"),
    _match("Nirvana",   "Smells Like", "/lib/Nirvana/Smells.mp3"),
    _match("Daft Punk", "Get Lucky",   "/lib/DaftPunk/GetLucky.mp3"),
]
HISTORY = [
    _entry("Radiohead", "Creep",       plays=10, timestamp="2020-01-01"),
    _entry("Nirvana",   "Smells Like", plays=5,  timestamp="2021-06-01"),
    _entry("Daft Punk", "Get Lucky",   plays=2,  timestamp="2019-03-01"),
]
LIBRARY = [
    _lib("Radiohead", "Creep",       "/lib/Radiohead/Creep.mp3"),
    _lib("Nirvana",   "Smells Like", "/lib/Nirvana/Smells.mp3"),
    _lib("Daft Punk", "Get Lucky",   "/lib/DaftPunk/GetLucky.mp3"),
    _lib("Unknown",   "Fresh Track", "/lib/Unknown/Fresh.mp3"),   # not in history
]


def _read_tracks(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [l for l in lines if l and not l.startswith("#")]


class TestListenAgain(unittest.TestCase):

    def test_file_created(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_listen_again(MATCHED, HISTORY, size=10, output_dir=Path(d))
            self.assertTrue(p.exists())

    def test_most_played_first(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_listen_again(MATCHED, HISTORY, size=10, output_dir=Path(d))
            tracks = _read_tracks(p)
        self.assertGreater(len(tracks), 0)
        self.assertEqual(tracks[0], "/lib/Radiohead/Creep.mp3")

    def test_size_limit_respected(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_listen_again(MATCHED, HISTORY, size=2, output_dir=Path(d))
            tracks = _read_tracks(p)
        self.assertLessEqual(len(tracks), 2)

    def test_extm3u_header(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_listen_again(MATCHED, HISTORY, size=5, output_dir=Path(d))
            content = p.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("#EXTM3U"))

    def test_empty_input_no_crash(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_listen_again([], [], size=10, output_dir=Path(d))
            self.assertTrue(p.exists())
            self.assertEqual(_read_tracks(p), [])


class TestFavorites(unittest.TestCase):

    def test_file_created(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_favorites(MATCHED, HISTORY, size=10, output_dir=Path(d))
            self.assertTrue(p.exists())

    def test_empty_input_no_crash(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_favorites([], [], size=10, output_dir=Path(d))
            self.assertTrue(p.exists())


class TestFreshRotation(unittest.TestCase):

    def test_excludes_matched_tracks(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_fresh_rotation(MATCHED, LIBRARY, size=10, output_dir=Path(d))
            tracks = _read_tracks(p)
        self.assertIn("/lib/Unknown/Fresh.mp3", tracks)
        self.assertNotIn("/lib/Radiohead/Creep.mp3", tracks)

    def test_empty_library_no_crash(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_fresh_rotation(MATCHED, [], size=10, output_dir=Path(d))
            self.assertTrue(p.exists())


class TestRediscovery(unittest.TestCase):

    def test_file_created(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_rediscovery(MATCHED, HISTORY, size=10,
                                     rediscovery_days=30, output_dir=Path(d))
            self.assertTrue(p.exists())

    def test_old_timestamps_qualify(self):
        # All HISTORY timestamps are years old → all should qualify
        with tempfile.TemporaryDirectory() as d:
            p = generate_rediscovery(MATCHED, HISTORY, size=10,
                                     rediscovery_days=30, output_dir=Path(d))
            tracks = _read_tracks(p)
        self.assertGreater(len(tracks), 0)

    def test_recent_track_excluded(self):
        from datetime import datetime, timezone
        recent_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        history_with_recent = HISTORY + [_entry("Radiohead", "Creep", timestamp=recent_ts)]
        matched_single = [MATCHED[0]]  # just Radiohead/Creep
        with tempfile.TemporaryDirectory() as d:
            p = generate_rediscovery(matched_single, history_with_recent,
                                     size=10, rediscovery_days=30, output_dir=Path(d))
            tracks = _read_tracks(p)
        self.assertNotIn("/lib/Radiohead/Creep.mp3", tracks)


class TestEnergyMix(unittest.TestCase):

    def test_file_created(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_energy_mix(MATCHED, LIBRARY, HISTORY, size=10,
                                    output_dir=Path(d))
            self.assertTrue(p.exists())

    def test_no_crash_on_empty(self):
        with tempfile.TemporaryDirectory() as d:
            p = generate_energy_mix([], [], [], size=10, output_dir=Path(d))
            self.assertTrue(p.exists())


class TestGenerateAll(unittest.TestCase):

    def test_all_five_playlists_written(self):
        with tempfile.TemporaryDirectory() as d:
            paths = generate_all(
                MATCHED, [], LIBRARY, HISTORY,
                size=10, rediscovery_days=30, output_dir=d,
            )
        self.assertEqual(len(paths), 5)
        names = {Path(p).stem for p in paths}
        self.assertEqual(names, {
            "listen_again", "favorites", "rediscovery",
            "fresh_rotation", "energy_mix",
        })


if __name__ == "__main__":
    unittest.main()
