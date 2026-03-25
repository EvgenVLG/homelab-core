# music-assistant

A local-only music assistant that reads your listening history, scans your
local audio library, matches them together, and generates practical `.m3u`
playlists — no cloud, no LLM, no database server required.

Runs in a single Docker container. Designed to integrate into the
[house-bot](https://github.com/you/homelab-core) homelab ecosystem.

---

## Folder structure

```
music-assistant/
  app/
    cli.py            Argparse subcommand entrypoint
    config.py         Config loaded from environment variables
    ingest.py         History file readers (JSON, CSV, Google Takeout)
    library_scan.py   Recursive audio file scanner
    normalize.py      String normalization used everywhere
    match_engine.py   Scoring-based history ↔ library matcher
    playlists.py      Five playlist generators → .m3u files
    stats.py          Summary stats + CSV/JSON output writers
    models.py         Dataclasses: HistoryEntry, LibraryTrack, MatchResult
    logging_setup.py  Single logging.basicConfig call
  data/
    input/            Drop your export files here
    library/          Symlink or mount your music root here
    output/           All generated output lands here
  tests/
    test_normalize.py
    test_match_engine.py
    test_ingest.py
    test_playlists.py
  Dockerfile
  compose.yaml
  requirements.txt
  .env.example
  README.md
```

---

## Supported input formats

Place files in `data/input/`. Mixed formats are fine — the ingestor picks
the right parser per file.

| Format | Detected by | Notes |
|--------|-------------|-------|
| Google Takeout `watch-history.json` | Presence of `"header"` key | Standard YouTube Music export |
| Generic JSON array | Any `.json` without `"header"` | Objects need `artist` + `track`/`title` |
| CSV | `.csv` extension | Columns: `artist`, `track`/`title`, optional `album`, `timestamp`, `play_count` |

Malformed or unrecognised files are logged and skipped — they never crash
the run. Check `LOG_LEVEL=DEBUG` output to see what was skipped and why.

### Getting your Google Takeout export

1. Go to [takeout.google.com](https://takeout.google.com)
2. Deselect all → select **YouTube and YouTube Music**
3. Under format options, keep JSON
4. Download and unzip
5. Find `Takeout/YouTube and YouTube Music/history/watch-history.json`
6. Drop it into `data/input/`

---

## How matching works

1. **Normalise** — every artist/track string is lowercased, Unicode-folded
   to ASCII, stripped of `feat.`/`ft.`/`(...)` noise, and punctuation is
   removed. The same `normalize()` function is used on both sides, so
   differences in quoting, accents, or featuring credits don't matter.

2. **Deduplicate history** — entries with the same normalised
   `(artist, track)` key are merged, summing `play_count` and keeping the
   most recent timestamp.

3. **Score each pair** — for each unique history entry, every library track
   is scored:

   | Signal | Weight | How |
   |--------|--------|-----|
   | Artist token overlap | 0.45 | Jaccard-style token intersection |
   | Track title similarity | 0.55 | Max of: difflib ratio + token overlap |

4. **Accept or reject** — the best-scoring library track wins if its score
   ≥ `MATCH_THRESHOLD` (default `0.6`). Lower to catch more tracks at the
   cost of false positives; raise for stricter matching.

5. **Record reason** — each `MatchResult` includes a human-readable `reason`
   field (e.g. `artist_overlap=0.80; title_ratio=0.75`) written to
   `matched_tracks.csv` for auditing.

6. **Unmatched saved** — entries with no qualifying match go to
   `unmatched_history.csv`. Review this file to find tracks worth adding to
   your library or to tune the threshold.

---

## Playlist heuristics

| Playlist | Logic |
|----------|-------|
| `listen_again` | Matched tracks sorted by total play count, descending |
| `favorites` | Matched tracks whose play count is in the top 25th percentile |
| `rediscovery` | Matched tracks not played in the last `REDISCOVERY_DAYS` days (or with no timestamp) — shuffled |
| `fresh_rotation` | Library tracks that never appeared in history — shuffled |
| `energy_mix` | Tracks scored by: genre folder keyword match (+1 for rock/dance/metal/electronic; −2 for ambient/classical/acoustic) + repeat-play bonus (capped at +1). Falls back to most-played if too few qualify. |

All five playlists are written even if some are empty — an empty `.m3u` is
better than a missing file.

---

## Running with Docker Compose

```bash
# 1. Edit compose.yaml: point LIBRARY_DIR at your real music root
#    (or change the left-hand side of the library volume mount)

# 2. Drop export files into data/input/

# 3. Build and run
docker compose build
docker compose run --rm music-assistant run-all

# Output lands in data/output/
ls data/output/
# library_index.csv  matched_tracks.csv  unmatched_history.csv
# summary.json       playlists/
```

### Running individual steps

```bash
docker compose run --rm music-assistant ingest
docker compose run --rm music-assistant scan-library
docker compose run --rm music-assistant match
docker compose run --rm music-assistant generate-playlists
docker compose run --rm music-assistant stats
```

### Running without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export INPUT_DIR=./data/input
export LIBRARY_DIR=/path/to/your/music
export OUTPUT_DIR=./data/output

python -m app.cli run-all
```

---

## Output files

| File | Contents |
|------|----------|
| `output/library_index.csv` | All scanned audio files with inferred metadata |
| `output/matched_tracks.csv` | Successful matches with score and match reason |
| `output/unmatched_history.csv` | History entries with no library match |
| `output/summary.json` | Counts, match rate, playlist names |
| `output/playlists/listen_again.m3u` | Most-played matched tracks |
| `output/playlists/favorites.m3u` | Top-quartile play-count tracks |
| `output/playlists/rediscovery.m3u` | Old favourites not recently played |
| `output/playlists/fresh_rotation.m3u` | Library tracks never in history |
| `output/playlists/energy_mix.m3u` | Heuristic higher-energy selection |

---

## Running tests

```bash
python -m pytest tests/ -v
```

No extra test dependencies — uses only the standard library.

---

## Configuration reference

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_DIR` | `/data/input` | History export files |
| `LIBRARY_DIR` | `/data/library` | Local music root |
| `OUTPUT_DIR` | `/data/output` | All generated output |
| `MATCH_THRESHOLD` | `0.6` | Minimum match score (0.0–1.0) |
| `AUDIO_EXTENSIONS` | `.mp3,.flac,…` | Extensions to index |
| `PLAYLIST_SIZE` | `30` | Max tracks per playlist |
| `REDISCOVERY_DAYS` | `90` | Days of silence → rediscovery eligible |
| `LOG_LEVEL` | `INFO` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` |

---

## Optional: tag reading

Install `mutagen` for better artist/title extraction from file tags:

```
# requirements.txt — uncomment:
mutagen==1.47.*
```

The scanner falls back to path-based inference (`Artist/Album/Track.mp3`
directory convention) without it. Tag data improves match quality on
libraries where filenames are messy.

---

## Limitations

- **Matching is approximate.** Live versions, remasters with very different
  names, and tracks with non-Latin titles may be missed. Review
  `unmatched_history.csv` to identify gaps.
- **O(H × L) matching.** For very large libraries (>50k tracks) this becomes
  slow. Acceptable for home use; can be sped up with a pre-built token index.
- **Energy mix is a proxy.** Genre folder names and repeat-play counts are
  cheap heuristics. No BPM, key, or audio feature analysis is performed.
- **Timestamps are best-effort.** Rediscovery and recency signals degrade
  gracefully when timestamps are absent.
- **No tag writing.** Playlists reference files by their existing paths;
  nothing is renamed, moved, or retagged.
- **No persistent state.** Each run re-processes everything. Fast enough for
  typical home library sizes.

## Next steps (not in v0.1)

- `/playlist` Telegram command in house-bot
- n8n webhook to trigger regeneration on new history export
- Navidrome playlist sync via its REST API
- `mutagen` tag writing to fix mismatched metadata
- BPM/energy from audio fingerprinting (essentia or librosa, opt-in)
