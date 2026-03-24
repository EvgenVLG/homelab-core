#!/usr/bin/env bash
set -Eeuo pipefail

cd /srv/docker/music-assistant

echo "=== app/ingest.py ==="
sed -n '1,260p' app/ingest.py || true
echo

echo "=== app/library_scan.py ==="
sed -n '1,260p' app/library_scan.py || true
echo

echo "=== app/match_engine.py ==="
sed -n '1,260p' app/match_engine.py || true
echo

echo "=== app/playlists.py ==="
sed -n '1,260p' app/playlists.py || true
echo

echo "=== app/stats.py ==="
sed -n '1,260p' app/stats.py || true
echo

echo "=== app/models.py ==="
sed -n '1,260p' app/models.py || true
echo

echo "=== dataclass / NamedTuple / class search ==="
grep -RniE '(@dataclass|NamedTuple|class HistoryEntry|class LibraryTrack|class MatchedTrack)' app || true
