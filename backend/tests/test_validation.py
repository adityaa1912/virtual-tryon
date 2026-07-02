import asyncio
import io

import pytest
from fastapi import UploadFile

from app.core.exceptions import (
    CorruptImageError,
    DecompressionBombError,
    EmptyFileError,
    FileTooLargeError,
    ImageDimensionError,
    UnsupportedMediaTypeError,
)
from app.services.validation_service import ImageValidationPolicy, ImageValidator
from tests.factories import jpeg_bytes, png_bytes


def make_policy(**overrides) -> ImageValidationPolicy:
    defaults = dict(
        allowed_mime_types=frozenset({"image/jpeg", "image/png", "image/webp"}),
        max_size_bytes=10 * 1024 * 1024,
        max_dimension=4096,
        max_pixels=40_000_000,
        read_chunk_size=1024 * 1024,
    )
    defaults.update(overrides)
    return ImageValidationPolicy(**defaults)


def upload(data: bytes, filename: str = "image.png") -> UploadFile:
    return UploadFile(file=io.BytesIO(data), filename=filename)


def validate(policy: ImageValidationPolicy, data: bytes, filename: str = "image.png"):
    return asyncio.run(ImageValidator(policy).validate(upload(data, filename)))


def test_accepts_valid_png():
    result = validate(make_policy(), png_bytes(64, 64))
    assert result.content_type == "image/png"
    assert result.extension == ".png"
    assert result.width == 64 and result.height == 64
    assert result.size_bytes == len(result.content)
    assert len(result.sha256) == 64


def test_accepts_valid_jpeg():
    result = validate(make_policy(), jpeg_bytes(100, 50), "image.jpg")
    assert result.content_type == "image/jpeg"
    assert result.extension == ".jpg"


def test_rejects_empty_file():
    with pytest.raises(EmptyFileError):
        validate(make_policy(), b"")


def test_rejects_spoofed_type():
    with pytest.raises(UnsupportedMediaTypeError):
        validate(make_policy(), b"this is plainly not an image")


def test_rejects_corrupt_image():
    with pytest.raises(CorruptImageError):
        validate(make_policy(), b"\x89PNG\r\n\x1a\n" + b"broken-tail")


def test_rejects_oversized_file():
    with pytest.raises(FileTooLargeError):
        validate(make_policy(max_size_bytes=100), png_bytes(256, 256))


def test_rejects_oversized_dimensions():
    with pytest.raises(ImageDimensionError):
        validate(make_policy(max_dimension=100), png_bytes(256, 256))


def test_rejects_decompression_bomb():
    with pytest.raises(DecompressionBombError):
        validate(make_policy(max_pixels=1000), png_bytes(256, 256))
