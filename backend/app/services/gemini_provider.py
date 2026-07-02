from abc import ABC, abstractmethod

from app.models.gemini import GeneratedImage, GeminiRequest


class GeminiProvider(ABC):
    @abstractmethod
    async def generate(self, request: GeminiRequest) -> GeneratedImage: ...


class FakeGeminiProvider(GeminiProvider):
    def __init__(
        self,
        *,
        image: GeneratedImage | None = None,
        error: Exception | None = None,
    ) -> None:
        self._image = image
        self._error = error

    async def generate(self, request: GeminiRequest) -> GeneratedImage:
        if self._error is not None:
            raise self._error
        if self._image is not None:
            return self._image
        person = request.parts[0].image
        return GeneratedImage(content=person.content, content_type=person.content_type)
