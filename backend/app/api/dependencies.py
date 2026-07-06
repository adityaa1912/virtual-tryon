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
from app.services.video_kling import KlingVideoProvider
from app.services.video_pollinations import PollinationsVideoProvider
from app.services.video_provider import FakeVideoProvider, VideoProvider
from app.services.video_veo import VeoVideoProvider
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
    if settings.gemini_provider != "google":
        return FakeGeminiProvider()
    if settings.gemini_use_vertex:
        if not settings.gemini_project_id:
            raise RuntimeError(
                "GEMINI_PROJECT_ID is required when GEMINI_USE_VERTEX is true."
            )
        return GoogleGeminiProvider(
            use_vertex=True,
            project_id=settings.gemini_project_id,
            location=settings.gemini_location,
        )
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is required when GEMINI_PROVIDER is 'google'."
        )
    return GoogleGeminiProvider(api_key=settings.gemini_api_key)


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


def get_video_provider(settings: Settings = Depends(get_settings)) -> VideoProvider:
    if settings.video_provider == "pollinations":
        if not settings.pollinations_api_key:
            raise RuntimeError(
                "POLLINATIONS_API_KEY is required when VIDEO_PROVIDER is "
                "'pollinations'."
            )
        return PollinationsVideoProvider(
            api_key=settings.pollinations_api_key,
            base_url=settings.pollinations_base_url,
            media_url=settings.pollinations_media_url,
            model=settings.pollinations_video_model,
            duration=settings.pollinations_duration,
            aspect_ratio=settings.pollinations_aspect_ratio,
            timeout_seconds=settings.pollinations_timeout_seconds,
        )
    if settings.video_provider == "veo":
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required when VIDEO_PROVIDER is 'veo'."
            )
        return VeoVideoProvider(
            api_key=settings.gemini_api_key,
            model=settings.veo_model,
            prompt=settings.veo_prompt,
            timeout_seconds=settings.veo_timeout_seconds,
            poll_interval_seconds=settings.veo_poll_interval_seconds,
        )
    if settings.video_provider == "kling":
        if not settings.kling_api_key:
            raise RuntimeError(
                "KLING_API_KEY is required when VIDEO_PROVIDER is 'kling'."
            )
        return KlingVideoProvider(
            api_key=settings.kling_api_key,
            base_url=settings.kling_base_url,
            model=settings.kling_model,
            poll_interval_seconds=settings.kling_poll_interval_seconds,
            poll_timeout_seconds=settings.kling_poll_timeout_seconds,
        )
    return FakeVideoProvider()


def get_video_service(
    storage: StorageProvider = Depends(get_storage_provider),
    provider: VideoProvider = Depends(get_video_provider),
) -> VideoService:
    return VideoService(storage=storage, provider=provider)
