from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidatedImage:
    content: bytes
    content_type: str
    extension: str
    size_bytes: int
    width: int
    height: int
    sha256: str
    original_filename: str | None
