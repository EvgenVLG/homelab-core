"""
String normalization used everywhere to make fuzzy matching consistent.

Strategy:
  - Unicode NFKD → ASCII-ish
  - lowercase
  - strip feat./ft./featuring and everything in parentheses/brackets
  - remove punctuation except spaces
  - collapse whitespace
  - optionally strip common noise words
"""
import re
import unicodedata

# Patterns stripped before comparison
_FEAT_RE = re.compile(
    r"\s*[\(\[]?(?:feat|ft|featuring|with)\.?\s+[^\)\]]*[\)\]]?",
    re.IGNORECASE,
)
_PAREN_RE = re.compile(r"[\(\[].*?[\)\]]")
_PUNCT_RE = re.compile(r"[^\w\s]")
_SPACE_RE = re.compile(r"\s+")

# Words that carry no signal for matching
_NOISE = frozenset(
    [
        "the", "a", "an", "and", "&", "remastered", "remaster",
        "official", "video", "audio", "hd", "4k", "lyrics", "explicit",
        "version", "edition", "deluxe", "bonus", "track",
    ]
)


def normalize(text: str, remove_noise: bool = False) -> str:
    """Return a normalized, comparable string."""
    if not text:
        return ""
    # Unicode NFKD decomposition → best-effort ASCII
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = _FEAT_RE.sub("", text)
    text = _PAREN_RE.sub("", text)
    text = _PUNCT_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    if remove_noise:
        text = " ".join(w for w in text.split() if w not in _NOISE)
    return text


def token_set(text: str) -> frozenset[str]:
    """Return frozenset of normalized, noise-stripped tokens."""
    return frozenset(normalize(text, remove_noise=True).split())
