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
