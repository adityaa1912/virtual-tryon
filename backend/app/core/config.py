from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "virtual-tryon-api"
    app_version: str = "0.1.0"

    max_upload_size_bytes: int = 10 * 1024 * 1024
    allowed_image_mime_types: str = "image/jpeg,image/png,image/webp"
    max_image_dimension: int = 4096
    max_image_pixels: int = 40_000_000
    upload_read_chunk_size: int = 1024 * 1024

    storage_dir: str = "storage"

    gemini_provider: str = "fake"
    gemini_use_vertex: bool = False
    gemini_api_key: str | None = None
    gemini_project_id: str | None = None
    gemini_location: str = "us-central1"
    gemini_model: str = "gemini-2.5-flash-image"
    gemini_temperature: float = 0.2
    gemini_top_p: float = 0.95
    gemini_candidate_count: int = 1
    gemini_response_modalities: str = "IMAGE"
    gemini_safety_threshold: str = "BLOCK_ONLY_HIGH"
    gemini_timeout_seconds: float = 60.0
    gemini_max_retries: int = 3

    preprocess_max_dimension: int = 1536

    video_provider: str = "fake"
    kling_api_key: str | None = None
    kling_base_url: str = "https://api-singapore.klingai.com"
    kling_model: str = "kling-v1"
    kling_poll_interval_seconds: float = 5.0
    kling_poll_timeout_seconds: float = 300.0

    @property
    def allowed_image_mime_type_set(self) -> frozenset[str]:
        return frozenset(
            item.strip()
            for item in self.allowed_image_mime_types.split(",")
            if item.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
