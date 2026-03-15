async function loadMusicStatus() {
  try {
    const res = await fetch("https://n8n.home.arpa/webhook/homelab-status");
    const data = await res.json();

    const existing = document.getElementById("music-status-box");
    if (existing) existing.remove();

    const dlMbps = ((data.qbittorrent?.dl_info_speed || 0) / 1024 / 1024).toFixed(2);
    const upMbps = ((data.qbittorrent?.up_info_speed || 0) / 1024 / 1024).toFixed(2);

    const statusColor = (value) => value === "ok" ? "#22c55e" : "#f59e0b";

    const box = document.createElement("div");
    box.id = "music-status-box";

    box.innerHTML = `
      <div class="music-status-title">🎧 Music Stack</div>

      <div class="music-status-line">
        <span class="music-label">Navidrome</span>
        <span class="music-badge" style="background:${statusColor(data.navidrome?.status)}">${data.navidrome?.status || "unknown"}</span>
      </div>

      <div class="music-status-line">
        <span class="music-label">Lidarr</span>
        <span class="music-badge" style="background:${statusColor(data.lidarr?.status)}">${data.lidarr?.status || "unknown"}</span>
      </div>

      <div class="music-status-line">
        <span class="music-label">Prowlarr</span>
        <span class="music-badge" style="background:${statusColor(data.prowlarr?.status)}">${data.prowlarr?.status || "unknown"}</span>
      </div>

      <div class="music-status-line">
        <span class="music-label">qBittorrent</span>
        <span class="music-badge" style="background:${statusColor(data.qbittorrent?.status)}">${data.qbittorrent?.status || "unknown"}</span>
      </div>

      <hr class="music-divider">

      <div class="music-status-line">
        <span class="music-label">DL</span>
        <span>${dlMbps} MB/s</span>
      </div>

      <div class="music-status-line">
        <span class="music-label">UP</span>
        <span>${upMbps} MB/s</span>
      </div>

      <div class="music-status-line">
        <span class="music-label">DHT</span>
        <span>${data.qbittorrent?.dht_nodes ?? 0}</span>
      </div>

      <div class="music-status-line">
        <span class="music-label">Conn</span>
        <span>${data.qbittorrent?.connection_status || "unknown"}</span>
      </div>

      <div class="music-status-time">Updated: ${data.updated || ""}</div>
    `;

    document.body.appendChild(box);
  } catch (err) {
    console.error("Music status load failed:", err);
  }
}

window.addEventListener("load", loadMusicStatus);
