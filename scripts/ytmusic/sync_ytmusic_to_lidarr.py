from ytmusicapi import YTMusic
import requests
import json
import os
from pathlib import Path
from datetime import datetime

# ---------- CONFIG ----------

LIDARR_URL = "http://127.0.0.1:8686"
LIDARR_API_KEY = "729d5bfbe57341ffa0659d29fe1b6f61"

ROOT_FOLDER = "/music"
QUALITY_PROFILE_ID = 1
METADATA_PROFILE_ID = 1

MAX_MIX_ARTISTS = 5
MAX_LIKED_SONGS = 500

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

STATE_FILE = Path("state.json")

# ---------- STATE ----------

if STATE_FILE.exists():
    state = json.loads(STATE_FILE.read_text())
else:
    state = {
        "artists_added": []
    }

# ---------- STATS ----------

stats = {
    "liked_tracks_scanned": 0,
    "liked_artists_found": 0,
    "mix_artists_found": 0,
    "artists_checked": 0,
    "artists_skipped_state": 0,
    "artists_no_lookup": 0,
    "artists_added": 0,
    "artists_failed": 0,
}

# ---------- INIT ----------

yt = YTMusic("headers_auth.json")


def log(msg: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


def lidarr_lookup_artist(name: str):
    url = f"{LIDARR_URL}/api/v1/artist/lookup"
    r = requests.get(
        url,
        headers={"X-Api-Key": LIDARR_API_KEY},
        params={"term": name},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def lidarr_add_artist(artist: dict) -> bool:
    payload = {
        "artistName": artist["artistName"],
        "foreignArtistId": artist["foreignArtistId"],
        "rootFolderPath": ROOT_FOLDER,
        "qualityProfileId": QUALITY_PROFILE_ID,
        "metadataProfileId": METADATA_PROFILE_ID,
        "monitored": True,
        "addOptions": {
            "searchForMissingAlbums": True
        }
    }

    if DRY_RUN:
        log(f"[DRY RUN] Would add artist: {artist['artistName']}")
        return True

    r = requests.post(
        f"{LIDARR_URL}/api/v1/artist",
        headers={"X-Api-Key": LIDARR_API_KEY},
        json=payload,
        timeout=30,
    )

    if r.status_code in (200, 201):
        log(f"Added artist: {artist['artistName']}")
        return True

    log(f"Failed to add artist: {artist['artistName']} | status={r.status_code} | response={r.text[:300]}")
    return False


def process_artist(name: str) -> None:
    stats["artists_checked"] += 1
    log(f"Checking artist: {name}")

    if name in state["artists_added"]:
        stats["artists_skipped_state"] += 1
        log(f"Skipping, already in state: {name}")
        return

    try:
        results = lidarr_lookup_artist(name)
    except Exception as e:
        stats["artists_failed"] += 1
        log(f"Lidarr lookup failed for {name}: {e}")
        return

    if not results:
        stats["artists_no_lookup"] += 1
        log(f"No Lidarr lookup results for: {name}")
        return

    artist = results[0]

    ok = lidarr_add_artist(artist)

    if ok:
        state["artists_added"].append(name)
        stats["artists_added"] += 1


# ---------- LIKED SONGS ----------

log("Scanning liked songs")

liked = yt.get_liked_songs(limit=MAX_LIKED_SONGS)["tracks"]
stats["liked_tracks_scanned"] = len(liked)

liked_artists = set()
for track in liked:
    if track.get("artists"):
        liked_artists.add(track["artists"][0]["name"])

stats["liked_artists_found"] = len(liked_artists)

for artist in sorted(liked_artists):
    process_artist(artist)

# ---------- YOUR MIX ----------

log("Scanning Your Mix")

home = yt.get_home()
mix_artists = set()

for section in home:
    if "contents" not in section:
        continue

    for item in section["contents"]:
        if item.get("playlistType") == "MIX":
            try:
                tracks = yt.get_playlist(item["playlistId"], limit=50)["tracks"]
            except Exception as e:
                log(f"Failed to read mix playlist: {e}")
                continue

            for t in tracks:
                if t.get("artists"):
                    mix_artists.add(t["artists"][0]["name"])

mix_artists = sorted(list(mix_artists))[:MAX_MIX_ARTISTS]
stats["mix_artists_found"] = len(mix_artists)

for artist in mix_artists:
    process_artist(artist)

# ---------- SAVE STATE ----------

STATE_FILE.write_text(json.dumps(state, indent=2))

# ---------- SUMMARY ----------

log("---------- SUMMARY ----------")
for k, v in stats.items():
    log(f"{k}: {v}")
log(f"dry_run: {DRY_RUN}")
log("Done")
