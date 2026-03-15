async function loadMusicStatus() {
  try {
    const res = await fetch("https://n8n.home.arpa/webhook/homelab-status");
    const data = await res.json();

    const existing = document.getElementById("music-status-box");
    if (existing) existing.remove();

    const box = document.createElement("div");
    box.id = "music-status-box";

    box.innerHTML = `
      <div class="music-status-title">🎧 Music Stack</div>
      <div class="music-status-line">Navidrome: ${data.navidrome?.status || "unknown"}</div>
      <div class="music-status-line">Lidarr: ${data.lidarr?.status || "unknown"} ${data.lidarr?.version ? `(${data.lidarr.version})` : ""}</div>
      <div class="music-status-line">Prowlarr: ${data.prowlarr?.status || "unknown"} ${data.prowlarr?.version ? `(${data.prowlarr.version})` : ""}</div>
      <div class="music-status-time">Updated: ${data.updated || ""}</div>
    `;

    document.body.appendChild(box);
  } catch (err) {
    console.error("Music status load failed:", err);
  }
}

window.addEventListener("load", loadMusicStatus);
