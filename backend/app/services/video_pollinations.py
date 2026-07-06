import logging
from urllib.parse import quote

from app.core.exceptions import VideoError, VideoRateLimitError, VideoTimeoutError
from app.services.video_provider import GeneratedVideo, VideoProvider

logger = logging.getLogger(__name__)

_MOTION_PROMPT = (
    "The person naturally wears the jewellery. The camera stays still while the "
    "subject gently turns their head and smiles."
)

# ASSUMPTION: Pollinations does not document the image-to-video parameter name.
# "image" mirrors the documented image-to-image parameter. Change this single
# value if the video endpoint expects a different parameter.
_IMAGE_PARAM = "image"


class PollinationsVideoProvider(VideoProvider):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        media_url: str,
        model: str,
        duration: int,
        aspect_ratio: str,
        timeout_seconds: float,
        transport=None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._media_url = media_url.rstrip("/")
        self._model = model
        self._duration = duration
        self._aspect_ratio = aspect_ratio
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def generate(self, image: bytes, image_content_type: str) -> GeneratedVideo:
        import httpx

        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds, transport=self._transport
            ) as client:
                image_url = await self._upload_image(
                    client, headers, image, image_content_type
                )
                logger.info("Generating Pollinations video with model %s", self._model)
                video = await self._request_video(client, headers, image_url)
        except httpx.TimeoutException as exc:
            raise VideoTimeoutError() from exc
        except httpx.HTTPError as exc:
            logger.warning("Pollinations transport error: %s", type(exc).__name__)
            raise VideoError("Pollinations request failed.") from exc
        return GeneratedVideo(content=video, content_type="video/mp4")

    async def _upload_image(self, client, headers, image: bytes, content_type) -> str:
        files = {"file": ("image.png", image, content_type or "image/png")}
        response = await client.post(
            f"{self._media_url}/upload", headers=headers, files=files
        )
        self._raise_for_status(response)
        return self._extract_media_url(response)

    async def _request_video(self, client, headers, image_url: str) -> bytes:
        params = {
            "model": self._model,
            "duration": self._duration,
            "aspectRatio": self._aspect_ratio,
            _IMAGE_PARAM: image_url,
        }
        url = f"{self._base_url}/video/{quote(_MOTION_PROMPT)}"
        response = await client.get(url, headers=headers, params=params)
        self._raise_for_status(response)
        if not response.headers.get("content-type", "").startswith("video/"):
            raise VideoError("Pollinations did not return a video.")
        return response.content

    def _extract_media_url(self, response) -> str:
        try:
            data = response.json()
        except ValueError:
            text = response.text.strip()
            if text.startswith("http"):
                return text
            raise VideoError("Pollinations upload did not return a media URL.")
        for key in ("url", "mediaUrl", "media_url"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value
        for key in ("hash", "cid", "id"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return f"{self._media_url}/{value}"
        raise VideoError("Pollinations upload did not return a media URL.")

    def _raise_for_status(self, response) -> None:
        if response.status_code < 400:
            return
        if response.status_code == 429:
            raise VideoRateLimitError()
        if response.status_code >= 500:
            raise VideoError("Pollinations service returned a server error.")
        raise VideoError(self._error_message(response))

    def _error_message(self, response) -> str:
        try:
            message = response.json().get("error", {}).get("message")
        except ValueError:
            message = None
        if isinstance(message, str) and message:
            return f"Pollinations request failed: {message}"
        return f"Pollinations request failed with status {response.status_code}."
