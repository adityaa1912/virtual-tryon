from functools import lru_cache
from pathlib import Path

from fastapi import Depends, File, UploadFile

from app.core.config import Settings, get_settings
from app.models.upload import ValidatedImage
from app.services.storage_service import LocalStorageProvider, StorageProvider
from app.services.validation_service import ImageValidationPolicy, ImageValidator


def get_image_validator(settings: Settings = Depends(get_settings)) -> ImageValidator:
    policy = ImageValidationPolicy(
        allowed_mime_types=settings.allowed_image_mime_type_set,
        max_size_bytes=settings.max_upload_size_bytes,
        max_dimension=settings.max_image_dimension,
        max_pixels=settings.max_image_pixels,
        read_chunk_size=settings.upload_read_chunk_size,
    )
    return ImageValidator(policy)


async def validate_image_upload(
    file: UploadFile = File(...),
    validator: ImageValidator = Depends(get_image_validator),
) -> ValidatedImage:
    return await validator.validate(file)


@lru_cache
def _build_storage_provider(root: str) -> StorageProvider:
    return LocalStorageProvider(Path(root))


def get_storage_provider(settings: Settings = Depends(get_settings)) -> StorageProvider:
    return _build_storage_provider(settings.storage_dir)
