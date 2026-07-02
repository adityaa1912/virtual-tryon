from dataclasses import dataclass

from fastapi import UploadFile

from app.core.exceptions import (
    CorruptImageError,
    DecompressionBombError,
    EmptyFileError,
    FileTooLargeError,
    ImageDimensionError,
    UnsupportedMediaTypeError,
)
from app.models.upload import ValidatedImage
from app.utils.image_inspection import (
    compute_sha256,
    open_image_dimensions,
    verify_image_integrity,
)
from app.utils.image_signatures import EXTENSION_BY_MIME, sniff_mime_type


@dataclass(frozen=True, slots=True)
class ImageValidationPolicy:
    allowed_mime_types: frozenset[str]
    max_size_bytes: int
    max_dimension: int
    max_pixels: int
    read_chunk_size: int


class ImageValidator:
    def __init__(self, policy: ImageValidationPolicy) -> None:
        self._policy = policy

    async def validate(self, file: UploadFile) -> ValidatedImage:
        content = await self._read_within_limit(file)

        if not content:
            raise EmptyFileError()

        content_type = sniff_mime_type(content)
        if content_type is None or content_type not in self._policy.allowed_mime_types:
            raise UnsupportedMediaTypeError(self._policy.allowed_mime_types)

        width, height = self._decode_dimensions(content)

        if width > self._policy.max_dimension or height > self._policy.max_dimension:
            raise ImageDimensionError(self._policy.max_dimension)

        if width * height > self._policy.max_pixels:
            raise DecompressionBombError(self._policy.max_pixels)

        self._assert_not_corrupt(content)

        return ValidatedImage(
            content=content,
            content_type=content_type,
            extension=EXTENSION_BY_MIME[content_type],
            size_bytes=len(content),
            width=width,
            height=height,
            sha256=compute_sha256(content),
            original_filename=file.filename,
        )

    async def _read_within_limit(self, file: UploadFile) -> bytes:
        chunks: list[bytes] = []
        total = 0
        while chunk := await file.read(self._policy.read_chunk_size):
            total += len(chunk)
            if total > self._policy.max_size_bytes:
                raise FileTooLargeError(self._policy.max_size_bytes)
            chunks.append(chunk)
        await file.seek(0)
        return b"".join(chunks)

    def _decode_dimensions(self, content: bytes) -> tuple[int, int]:
        try:
            return open_image_dimensions(content)
        except Exception as exc:
            raise CorruptImageError() from exc

    def _assert_not_corrupt(self, content: bytes) -> None:
        try:
            verify_image_integrity(content)
        except Exception as exc:
            raise CorruptImageError() from exc
