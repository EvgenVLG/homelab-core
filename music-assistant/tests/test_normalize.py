import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.normalize import normalize, token_set


class TestNormalize(unittest.TestCase):

    def test_basic_lowercase(self):
        self.assertEqual(normalize("The Beatles"), "the beatles")

    def test_feat_stripped(self):
        result = normalize("Song feat. Someone Else")
        self.assertNotIn("feat", result)
        self.assertNotIn("someone", result)

    def test_feat_bracket_variant(self):
        result = normalize("Track (feat. Artist)")
        self.assertNotIn("feat", result)

    def test_paren_noise_stripped(self):
        result = normalize("Track (Remastered 2023)")
        self.assertNotIn("remastered", result)

    def test_bracket_noise_stripped(self):
        result = normalize("Track [Official Video]")
        self.assertNotIn("official", result)

    def test_punctuation_removed(self):
        result = normalize("It's a Wonderful Life!")
        self.assertNotIn("'", result)
        self.assertNotIn("!", result)

    def test_unicode_folded(self):
        self.assertEqual(normalize("Bjork"), "bjork")

    def test_token_set_overlap(self):
        a = token_set("Radiohead")
        b = token_set("Radiohead OK Computer")
        self.assertIn("radiohead", a & b)

    def test_empty_string(self):
        self.assertEqual(normalize(""), "")

    def test_whitespace_collapsed(self):
        self.assertEqual(normalize("too   many   spaces"), "too many spaces")

    def test_noise_words_removed(self):
        result = normalize("The Best Remastered", remove_noise=True)
        self.assertNotIn("the", result.split())
        self.assertNotIn("remastered", result.split())


if __name__ == "__main__":
    unittest.main()
