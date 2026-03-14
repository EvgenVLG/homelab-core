from ytmusicapi import YTMusic
import json

yt = YTMusic("headers_auth.json")

print("Getting liked songs...")

songs = yt.get_liked_songs(limit=5000)["tracks"]

result = []

for s in songs:
    artist = s["artists"][0]["name"] if s.get("artists") else None
    title = s.get("title")

    if artist and title:
        result.append({
            "artist": artist,
            "title": title
        })

print(f"Found {len(result)} songs")

with open("ytmusic_likes.json", "w") as f:
    json.dump(result, f, indent=2)

print("Saved to ytmusic_likes.json")
