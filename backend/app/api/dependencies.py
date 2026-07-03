from functools import lru_cache
from pathlib import Path

from fastapi import Depends, File, UploadFile

from app.core.config import Settings, get_settings
from app.models.gemini import GenerationConfig
from app.models.upload import ValidatedImage
from app.services.gemini_google import GoogleGeminiProvider
from app.services.gemini_provider import FakeGeminiProvider, GeminiProvider
from app.services.gemini_service import GeminiService
from app.services.image_preprocessor import ImagePreprocessor
from app.services.prompt_builder import PromptBuilder
from app.services.storage_service import LocalStorageProvider, StorageProvider
from app.services.tryon_service import TryOnService
from app.services.validation_service import ImageValidationPolicy, ImageValidator
from app.services.video_provider import FakeVideoProvider, VideoProvider
from app.services.video_service import VideoService


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


def get_generation_config(
    settings: Settings = Depends(get_settings),
) -> GenerationConfig:
    modalities = tuple(
        item.strip()
        for item in settings.gemini_response_modalities.split(",")
        if item.strip()
    )
    print("MODEL FROM SETTINGS:", settings.gemini_model)
    return GenerationConfig(
        model=settings.gemini_model,
        temperature=settings.gemini_temperature,
        top_p=settings.gemini_top_p,
        candidate_count=settings.gemini_candidate_count,
        response_modalities=modalities,
        safety_threshold=settings.gemini_safety_threshold,
        timeout_seconds=settings.gemini_timeout_seconds,
        max_retries=settings.gemini_max_retries,
    )


def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()


def get_gemini_provider(settings: Settings = Depends(get_settings)) -> GeminiProvider:
    if settings.gemini_provider == "google":
        print("Provider:", settings.gemini_provider)
        print("API Key loaded:", bool(settings.gemini_api_key))
        print("Using GoogleGeminiProvider")
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required when GEMINI_PROVIDER is 'google'."
            )
        return GoogleGeminiProvider(settings.gemini_api_key)
    return FakeGeminiProvider()


def get_gemini_service(
    provider: GeminiProvider = Depends(get_gemini_provider),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    generation_config: GenerationConfig = Depends(get_generation_config),
    output_validator: ImageValidator = Depends(get_image_validator),
) -> GeminiService:
    return GeminiService(
        provider=provider,
        prompt_builder=prompt_builder,
        generation_config=generation_config,
        output_validator=output_validator,
    )


def get_image_preprocessor(
    settings: Settings = Depends(get_settings),
) -> ImagePreprocessor:
    return ImagePreprocessor(settings.preprocess_max_dimension)


def get_tryon_service(
    storage: StorageProvider = Depends(get_storage_provider),
    preprocessor: ImagePreprocessor = Depends(get_image_preprocessor),
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> TryOnService:
    return TryOnService(
        storage=storage,
        preprocessor=preprocessor,
        gemini_service=gemini_service,
    )


def get_video_provider() -> VideoProvider:
    return FakeVideoProvider()


def get_video_service(
    storage: StorageProvider = Depends(get_storage_provider),
    provider: VideoProvider = Depends(get_video_provider),
) -> VideoService:
    return VideoService(storage=storage, provider=provider)
