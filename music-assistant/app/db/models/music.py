from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MusicSource(Base):
    __tablename__ = "music_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class HistoryImport(Base):
    __tablename__ = "history_imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("music_sources.id", ondelete="CASCADE"), nullable=False)
    import_type: Mapped[str] = mapped_column(String(64), nullable=False)
    input_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    stats_json: Mapped[str | None] = mapped_column(Text)
    error_text: Mapped[str | None] = mapped_column(Text)


class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    source_id: Mapped[int | None] = mapped_column(ForeignKey("music_sources.id", ondelete="SET NULL"))
    source_event_id: Mapped[str | None] = mapped_column(String(255))
    played_at: Mapped[datetime | None] = mapped_column(DateTime)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_artist: Mapped[str | None] = mapped_column(String(512))
    raw_title: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_album: Mapped[str | None] = mapped_column(String(512))
    canonical_artist: Mapped[str | None] = mapped_column(String(512))
    canonical_title: Mapped[str | None] = mapped_column(String(512))
    source_url: Mapped[str | None] = mapped_column(String(1024))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class LibraryTrack(Base):
    __tablename__ = "library_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("music_sources.id", ondelete="SET NULL"))
    file_path: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    file_hash: Mapped[str | None] = mapped_column(String(128))
    raw_artist: Mapped[str | None] = mapped_column(String(512))
    raw_title: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_album: Mapped[str | None] = mapped_column(String(512))
    clean_artist: Mapped[str | None] = mapped_column(String(512))
    clean_title: Mapped[str | None] = mapped_column(String(512))
    duration_sec: Mapped[int | None] = mapped_column(Integer)
    exists_flag: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_scanned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)


class TrackMatch(Base):
    __tablename__ = "track_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[int] = mapped_column(ForeignKey("listening_history.id", ondelete="CASCADE"), nullable=False)
    library_track_id: Mapped[int] = mapped_column(ForeignKey("library_tracks.id", ondelete="CASCADE"), nullable=False)
    match_status: Mapped[str] = mapped_column(String(32), nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    artist_score: Mapped[float] = mapped_column(Float, nullable=False)
    title_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    track_token_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class PlaylistRun(Base):
    __tablename__ = "playlist_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    run_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    params_json: Mapped[str | None] = mapped_column(Text)
    stats_json: Mapped[str | None] = mapped_column(Text)
    error_text: Mapped[str | None] = mapped_column(Text)


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    playlist_type: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_from_run_id: Mapped[int | None] = mapped_column(ForeignKey("playlist_runs.id", ondelete="SET NULL"))
    file_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    track_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PlaylistItem(Base):
    __tablename__ = "playlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    library_track_id: Mapped[int] = mapped_column(ForeignKey("library_tracks.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    reason: Mapped[str | None] = mapped_column(Text)


class MissingTrackQueue(Base):
    __tablename__ = "missing_tracks_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    canonical_artist: Mapped[str | None] = mapped_column(String(512))
    canonical_title: Mapped[str] = mapped_column(String(512), nullable=False)
    source_history_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    priority: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="OPEN", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
