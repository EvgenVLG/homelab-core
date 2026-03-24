from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "music-assistant"
    app_env: str = "dev"

    # Pipeline-compatible paths
    input_dir: Path = Field(default=Path("/data/input"), alias="INPUT_DIR")
    library_dir: Path = Field(default=Path("/data/library"), alias="LIBRARY_DIR")
    output_dir: Path = Field(default=Path("/data/output"), alias="OUTPUT_DIR")

    # Pipeline-compatible runtime settings
    match_threshold: float = Field(default=0.6, alias="MATCH_THRESHOLD")
    playlist_size: int = Field(default=30, alias="PLAYLIST_SIZE")
    rediscovery_days: int = Field(default=90, alias="REDISCOVERY_DAYS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Library scan settings
    audio_extensions: tuple[str, ...] = Field(
        default=(".mp3", ".flac", ".m4a", ".aac", ".ogg", ".wav"),
        alias="AUDIO_EXTENSIONS",
    )

    # DB / state
    data_root: Path = Path("/data")
    database_url: str = "sqlite:////data/state/music_assistant.db"

    # Foundation defaults
    default_timezone: str = "America/New_York"
    default_language: str = "en"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()
