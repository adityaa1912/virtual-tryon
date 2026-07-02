import asyncio

import pytest

from app.core.exceptions import GeminiInvalidOutputError, GeminiSafetyRefusalError
from app.models.gemini import (
    GeneratedImage,
    GenerationConfig,
    JewelleryCategory,
    NormalizedImage,
)
from app.prompts.tryon import TRYON_PROMPT_VERSION
from app.services.gemini_provider import FakeGeminiProvider
from app.services.gemini_service import GeminiService
from app.services.prompt_builder import PromptBuilder
from app.services.validation_service import ImageValidationPolicy, ImageValidator
from tests.factories import png_bytes


def make_config() -> GenerationConfig:
    return GenerationConfig(
        model="gemini-test",
        temperature=0.2,
        top_p=0.95,
        candidate_count=1,
        response_modalities=("IMAGE",),
        safety_threshold="BLOCK_ONLY_HIGH",
        timeout_seconds=30.0,
        max_retries=3,
    )


def make_validator() -> ImageValidator:
    return ImageValidator(
        ImageValidationPolicy(
            allowed_mime_types=frozenset({"image/jpeg", "image/png", "image/webp"}),
            max_size_bytes=10 * 1024 * 1024,
            max_dimension=4096,
            max_pixels=40_000_000,
            read_chunk_size=1024 * 1024,
        )
    )


def make_service(provider: FakeGeminiProvider) -> GeminiService:
    return GeminiService(
        provider=provider,
        prompt_builder=PromptBuilder(),
        generation_config=make_config(),
        output_validator=make_validator(),
    )


def normalized(data: bytes) -> NormalizedImage:
    return NormalizedImage(content=data, content_type="image/png")


def run_tryon(service: GeminiService):
    return asyncio.run(
        service.generate_tryon(
            normalized(png_bytes(64, 64)),
            normalized(png_bytes(32, 32)),
            JewelleryCategory.NECKLACE,
        )
    )


def test_generate_tryon_returns_validated_traceable_result():
    result = run_tryon(make_service(FakeGeminiProvider()))
    assert result.prompt_version == TRYON_PROMPT_VERSION
    assert result.model == "gemini-test"
    assert result.image.content_type == "image/png"
    assert result.image.width == 64 and result.image.height == 64
    assert len(result.image.sha256) == 64


def test_generate_tryon_propagates_safety_refusal():
    service = make_service(FakeGeminiProvider(error=GeminiSafetyRefusalError()))
    with pytest.raises(GeminiSafetyRefusalError):
        run_tryon(service)


def test_generate_tryon_rejects_invalid_output():
    provider = FakeGeminiProvider(
        image=GeneratedImage(content=b"not an image", content_type="image/png")
    )
    with pytest.raises(GeminiInvalidOutputError):
        run_tryon(make_service(provider))
