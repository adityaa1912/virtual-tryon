import random

import anyio

from app.core.exceptions import (
    GeminiEmptyResponseError,
    GeminiError,
    GeminiRateLimitError,
    GeminiSafetyRefusalError,
    GeminiServerError,
    GeminiTimeoutError,
)
from app.models.gemini import GeneratedImage, GeminiRequest, GenerationConfig
from app.services.gemini_provider import GeminiProvider

_SAFETY_CATEGORIES = (
    "HARM_CATEGORY_HARASSMENT",
    "HARM_CATEGORY_HATE_SPEECH",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "HARM_CATEGORY_DANGEROUS_CONTENT",
)

_RETRYABLE_ERRORS = (GeminiRateLimitError, GeminiTimeoutError, GeminiServerError)


def _is_retryable(error: Exception) -> bool:
    return isinstance(error, _RETRYABLE_ERRORS)


def _backoff_delay(attempt: int) -> float:
    return min(8.0, 0.5 * (2 ** (attempt - 1))) + random.uniform(0.0, 0.25)


class GoogleGeminiProvider(GeminiProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        use_vertex: bool = False,
        project_id: str | None = None,
        location: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._use_vertex = use_vertex
        self._project_id = project_id
        self._location = location
        self._client = None

    async def generate(self, request: GeminiRequest) -> GeneratedImage:
        contents = self._build_contents(request)
        sdk_config = self._build_config(request.config)
        response = await self._call_with_retry(request.config, contents, sdk_config)
        return self._extract_image(response)

    def _client_instance(self):
        if self._client is None:
            from google import genai

            if self._use_vertex:
                self._client = genai.Client(
                    vertexai=True,
                    project=self._project_id,
                    location=self._location,
                )
            else:
                self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _build_contents(self, request: GeminiRequest) -> list:
        from google.genai import types

        contents: list = []
        for part in request.parts:
            contents.append(f"{part.label}:")
            contents.append(
                types.Part.from_bytes(
                    data=part.image.content, mime_type=part.image.content_type
                )
            )
        contents.append(request.prompt_text)
        return contents

    def _build_config(self, config: GenerationConfig):
        from google.genai import types

        return types.GenerateContentConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            candidate_count=config.candidate_count,
            response_modalities=list(config.response_modalities),
            safety_settings=[
                types.SafetySetting(category=category, threshold=config.safety_threshold)
                for category in _SAFETY_CATEGORIES
            ],
        )

    async def _call_with_retry(self, config: GenerationConfig, contents, sdk_config):
        attempt = 0
        while True:
            try:
                print("=" * 80)
                print("MODEL SENT TO GOOGLE:", config.model)
                print("=" * 80)

                return await anyio.to_thread.run_sync(
                    lambda: self._client_instance().models.generate_content(
                        model=config.model, contents=contents, config=sdk_config
                    )
                )
            except Exception as exc:
                import traceback
                print("=" * 80)
                print("Exception type:", type(exc))
                print("Exception:", exc)
                traceback.print_exc()
                print("=" * 80)

                mapped = self._map_error(exc)
                attempt += 1
                if attempt > config.max_retries or not _is_retryable(mapped):
                    raise mapped from exc
                await anyio.sleep(_backoff_delay(attempt))

    def _map_error(self, exc: Exception) -> Exception:
        from google.genai import errors as genai_errors

        if isinstance(exc, genai_errors.APIError):
            code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
            if code == 429:
                return GeminiRateLimitError()
            if isinstance(code, int) and code >= 500:
                return GeminiServerError()
            return GeminiError(f"Gemini request failed: {exc}")
        if "timeout" in type(exc).__name__.lower() or isinstance(exc, TimeoutError):
            return GeminiTimeoutError()
        return GeminiError(f"Gemini request failed: {exc}")

    def _extract_image(self, response) -> GeneratedImage:
        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            raise GeminiEmptyResponseError()

        content = getattr(candidates[0], "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            inline = getattr(part, "inline_data", None)
            if inline is not None and getattr(inline, "data", None):
                return GeneratedImage(
                    content=inline.data, content_type=inline.mime_type
                )

        finish_reason = str(getattr(candidates[0], "finish_reason", "")).upper()
        if "SAFETY" in finish_reason:
            raise GeminiSafetyRefusalError()
        raise GeminiEmptyResponseError()
