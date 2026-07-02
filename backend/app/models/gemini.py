from dataclasses import dataclass
from enum import Enum

from app.models.upload import ValidatedImage


class JewelleryCategory(str, Enum):
    NECKLACE = "necklace"
    EARRINGS = "earrings"
    RING = "ring"
    BRACELET = "bracelet"
    WATCH = "watch"
    GLASSES = "glasses"


@dataclass(frozen=True, slots=True)
class NormalizedImage:
    content: bytes
    content_type: str


@dataclass(frozen=True, slots=True)
class GeminiImagePart:
    label: str
    image: NormalizedImage


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    model: str
    temperature: float
    top_p: float
    candidate_count: int
    response_modalities: tuple[str, ...]
    safety_threshold: str
    timeout_seconds: float
    max_retries: int


@dataclass(frozen=True, slots=True)
class BuiltPrompt:
    text: str
    version: str


@dataclass(frozen=True, slots=True)
class GeminiRequest:
    parts: tuple[GeminiImagePart, ...]
    prompt_text: str
    config: GenerationConfig


@dataclass(frozen=True, slots=True)
class GeneratedImage:
    content: bytes
    content_type: str


@dataclass(frozen=True, slots=True)
class TryOnResult:
    image: ValidatedImage
    prompt_version: str
    model: str
