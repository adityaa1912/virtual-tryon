from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeneratedVideo:
    content: bytes
    content_type: str


class VideoProvider(ABC):
    @abstractmethod
    async def generate(self, image: bytes, image_content_type: str) -> GeneratedVideo: ...


class FakeVideoProvider(VideoProvider):
    def __init__(
        self,
        *,
        video: GeneratedVideo | None = None,
        error: Exception | None = None,
    ) -> None:
        self._video = video
        self._error = error

    async def generate(self, image: bytes, image_content_type: str) -> GeneratedVideo:
        if self._error is not None:
            raise self._error
        if self._video is not None:
            return self._video
        return GeneratedVideo(content=_MINIMAL_MP4, content_type="video/mp4")


_MINIMAL_MP4 = bytes.fromhex(
    "0000001c667479706d70343200000000"
    "6d70343269736f6d000000086d646174"
)
