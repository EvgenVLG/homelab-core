import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.models import HistoryEntry, LibraryTrack
from app.match_engine import match, _deduplicate_history


def _entry(artist, track, plays=1, timestamp=""):
    return HistoryEntry(source="test", artist=artist, track=track,
                        play_count=plays, timestamp=timestamp)

def _track(artist, title, path=None):
    return LibraryTrack(
        path=path or f"/lib/{artist}/{title}.mp3",
        filename=title, artist=artist, album="Test Album",
        title=title, extension=".mp3",
    )


class TestMatching(unittest.TestCase):

    def test_exact_match(self):
        matched, unmatched = match([_entry("Radiohead", "Creep")],
                                   [_track("Radiohead", "Creep")])
        self.assertEqual(len(matched), 1)
        self.assertEqual(len(unmatched), 0)
        self.assertEqual(matched[0].library_path, "/lib/Radiohead/Creep.mp3")

    def test_case_insensitive(self):
        matched, _ = match([_entry("radiohead", "creep")],
                           [_track("Radiohead", "Creep")])
        self.assertEqual(len(matched), 1)

    def test_feat_noise_ignored(self):
        matched, _ = match(
            [_entry("Daft Punk", "Get Lucky feat. Pharrell Williams")],
            [_track("Daft Punk", "Get Lucky")],
        )
        self.assertEqual(len(matched), 1)

    def test_paren_noise_ignored(self):
        matched, _ = match(
            [_entry("Nirvana", "Come As You Are (Remastered)")],
            [_track("Nirvana", "Come As You Are")],
        )
        self.assertEqual(len(matched), 1)

    def test_no_match_different_artists(self):
        matched, unmatched = match([_entry("Artist A", "Track X")],
                                   [_track("Artist B", "Completely Different")])
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(unmatched), 1)

    def test_best_library_track_wins(self):
        matched, _ = match(
            [_entry("Radiohead", "Creep")],
            [_track("Radiohead", "Creep"), _track("Other", "Something Else")],
        )
        self.assertEqual(len(matched), 1)
        self.assertIn("Radiohead", matched[0].library_path)

    def test_match_score_recorded(self):
        matched, _ = match([_entry("Radiohead", "Creep")],
                           [_track("Radiohead", "Creep")])
        self.assertGreater(matched[0].score, 0.6)

    def test_match_reason_recorded(self):
        matched, _ = match([_entry("Radiohead", "Creep")],
                           [_track("Radiohead", "Creep")])
        self.assertIsInstance(matched[0].reason, str)
        self.assertGreater(len(matched[0].reason), 0)


class TestDeduplication(unittest.TestCase):

    def test_sums_play_counts(self):
        entries = [
            _entry("Radiohead", "Creep", plays=2, timestamp="2024-01-01"),
            _entry("Radiohead", "Creep", plays=3, timestamp="2024-06-01"),
        ]
        deduped = _deduplicate_history(entries)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].play_count, 5)

    def test_keeps_latest_timestamp(self):
        entries = [
            _entry("Radiohead", "Creep", timestamp="2023-01-01"),
            _entry("Radiohead", "Creep", timestamp="2024-06-01"),
        ]
        deduped = _deduplicate_history(entries)
        self.assertEqual(deduped[0].timestamp, "2024-06-01")

    def test_preserves_distinct_tracks(self):
        entries = [
            _entry("Radiohead", "Creep"),
            _entry("Radiohead", "Karma Police"),
        ]
        deduped = _deduplicate_history(entries)
        self.assertEqual(len(deduped), 2)

    def test_case_insensitive_dedup(self):
        entries = [
            _entry("radiohead", "creep", plays=1),
            _entry("Radiohead", "Creep", plays=1),
        ]
        deduped = _deduplicate_history(entries)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].play_count, 2)


if __name__ == "__main__":
    unittest.main()
