import logging
import time

import anyio

from app.core.exceptions import VideoError, VideoRateLimitError, VideoTimeoutError
from app.services.video_provider import GeneratedVideo, VideoProvider

logger = logging.getLogger(__name__)

_DEFAULT_MIME_TYPE = "image/png"


class VeoVideoProvider(VideoProvider):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        prompt: str,
        timeout_seconds: float,
        poll_interval_seconds: float,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._prompt = prompt
        self._timeout_seconds = timeout_seconds
        self._poll_interval = poll_interval_seconds
        self._client = None

    async def generate(self, image: bytes, image_content_type: str) -> GeneratedVideo:
        try:
            operation = await anyio.to_thread.run_sync(
                self._start_operation, image, image_content_type
            )
            operation = await self._await_completion(operation)
            content = await anyio.to_thread.run_sync(self._download, operation)
        except (VideoError, VideoTimeoutError, VideoRateLimitError):
            raise
        except Exception as exc:
            raise self._map_error(exc) from exc
        return GeneratedVideo(content=content, content_type="video/mp4")

    def _client_instance(self):
        if self._client is None:
            from google import genai
            from google.genai import types

            http_options = types.HttpOptions(
                timeout=int(self._timeout_seconds * 1000)
            )
            self._client = genai.Client(
                api_key=self._api_key, http_options=http_options
            )
        return self._client

    def _start_operation(self, image: bytes, image_content_type: str):
        from google.genai import types

        client = self._client_instance()
        logger.info("Submitting Veo video generation (model=%s)", self._model)
        return client.models.generate_videos(
            model=self._model,
            prompt=self._prompt,
            image=types.Image(
                image_bytes=image,
                mime_type=image_content_type or _DEFAULT_MIME_TYPE,
            ),
        )

    async def _await_completion(self, operation):
        deadline = time.monotonic() + self._timeout_seconds
        while not operation.done:
            if time.monotonic() >= deadline:
                raise VideoTimeoutError()
            await anyio.sleep(self._poll_interval)
            operation = await anyio.to_thread.run_sync(self._refresh, operation)
        if operation.error:
            logger.warning("Veo operation returned an error: %s", operation.error)
            raise VideoError("Veo video generation failed.")
        return operation

    def _refresh(self, operation):
        return self._client_instance().operations.get(operation)

    def _download(self, operation) -> bytes:
        client = self._client_instance()
        videos = getattr(operation.response, "generated_videos", None) or []
        if not videos:
            raise VideoError("Veo returned no video.")
        video = videos[0].video
        content = client.files.download(file=video)
        if not content:
            content = getattr(video, "video_bytes", None)
        if not content:
            raise VideoError("Veo returned an empty video.")
        self._ensure_mp4(content, getattr(video, "mime_type", None))
        return content

    def _ensure_mp4(self, content: bytes, mime_type: str | None) -> None:
        if mime_type and "mp4" not in mime_type.lower():
            raise VideoError(f"Veo returned unexpected media type: {mime_type}.")
        if len(content) < 12 or content[4:8] != b"ftyp":
            raise VideoError("Veo returned data that is not a valid MP4.")

    def _map_error(self, exc: Exception) -> Exception:
        import httpx
        from google.genai import errors

        if isinstance(exc, httpx.TimeoutException):
            return VideoTimeoutError()
        if isinstance(exc, errors.APIError):
            code = getattr(exc, "code", None)
            if code == 429:
                return VideoRateLimitError()
            return VideoError(f"Veo request failed (status {code}).")
        return VideoError("Veo video generation failed.")
