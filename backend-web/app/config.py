from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: str = "./watchlist.sqlite3"
    weights_path: str = "./models/weights.pt"
    cameras_json_path: str = "./app/data/cameras.json"

    poll_interval_seconds: int = 25
    inference_conf_threshold: float = 0.4
    open_inference_conf_threshold: float = 0.05
    open_classes: List[str] = Field(default_factory=lambda: ["open_parking"])
    occupied_classes: List[str] = Field(default_factory=lambda: ["parked_cars"])
    allowed_durations: List[int] = Field(default_factory=lambda: [30, 60, 90])

    dot_image_base: str = "https://webcams.nyctmc.org/api/cameras"
    dot_request_timeout_seconds: float = 10.0

    resend_api_key: str = ""
    resend_api_base: str = "https://api.resend.com"
    resend_request_timeout_seconds: float = 15.0
    from_email: str = "noreply@example.com"
    from_name: str = "Parking Spotter"
    public_site_url: str = "http://localhost:3000"

    shared_api_key: str = "change-me"
    allowed_cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    @field_validator("open_classes", "occupied_classes", "allowed_cors_origins", mode="before")
    @classmethod
    def _split_csv_strs(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("allowed_durations", mode="before")
    @classmethod
    def _split_csv_ints(cls, v):
        if isinstance(v, str):
            return [int(s.strip()) for s in v.split(",") if s.strip()]
        return v

    def resolved_db_path(self) -> Path:
        return Path(self.db_path).expanduser().resolve()

    def resolved_weights_path(self) -> Path:
        return Path(self.weights_path).expanduser().resolve()

    def resolved_cameras_path(self) -> Path:
        return Path(self.cameras_json_path).expanduser().resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
