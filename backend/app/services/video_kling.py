import base64
import time

from anyio import sleep

from app.core.exceptions import VideoError, VideoRateLimitError, VideoTimeoutError
from app.services.video_provider import GeneratedVideo, VideoProvider

_IMAGE2VIDEO_PATH = "/v1/videos/image2video"


class KlingVideoProvider(VideoProvider):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        poll_interval_seconds: float,
        poll_timeout_seconds: float,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._poll_interval = poll_interval_seconds
        self._poll_timeout = poll_timeout_seconds

    async def generate(self, image: bytes, image_content_type: str) -> GeneratedVideo:
        import httpx

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model_name": self._model,
            "image": base64.b64encode(image).decode("ascii"),
            "prompt": "The person naturally wears the jewellery. The camera remains still while the subject gently turns their head and smiles.",
            "mode": "std",
            "duration": "5",
        }
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url, timeout=30.0
            ) as client:
                task_id = await self._submit(client, headers, payload)
                video_url = await self._poll(client, headers, task_id)
                content = await self._download(client, video_url)
        except httpx.TimeoutException as exc:
            raise VideoTimeoutError() from exc
        except httpx.HTTPError as exc:
            raise VideoError("Kling request failed.") from exc
        return GeneratedVideo(content=content, content_type="video/mp4")

    async def _submit(self, client, headers: dict, payload: dict) -> str:
        response = await client.post(_IMAGE2VIDEO_PATH, headers=headers, json=payload)
        self._raise_for_status(response)
        task_id = response.json().get("data", {}).get("task_id")
        if not task_id:
            raise VideoError("Kling did not return a task id.")
        return task_id

    async def _poll(self, client, headers: dict, task_id: str) -> str:
        deadline = time.monotonic() + self._poll_timeout
        while True:
            response = await client.get(
                f"{_IMAGE2VIDEO_PATH}/{task_id}", headers=headers
            )
            self._raise_for_status(response)
            data = response.json().get("data", {})
            status = data.get("task_status")
            if status == "succeed":
                return self._extract_video_url(data)
            if status == "failed":
                raise VideoError(
                    data.get("task_status_msg") or "Kling video generation failed."
                )
            if time.monotonic() >= deadline:
                raise VideoTimeoutError()
            await sleep(self._poll_interval)

    async def _download(self, client, video_url: str) -> bytes:
        response = await client.get(video_url)
        self._raise_for_status(response)
        return response.content

    def _extract_video_url(self, data: dict) -> str:
        videos = (data.get("task_result") or {}).get("videos") or []
        if not videos or not videos[0].get("url"):
            raise VideoError("Kling response did not include a video URL.")
        return videos[0]["url"]

    def _raise_for_status(self, response) -> None:
        if response.status_code == 429:
            raise VideoRateLimitError()
        if response.status_code >= 500:
            raise VideoError("Kling service returned a server error.")
        if response.status_code >= 400:
            raise VideoError(
                f"Kling request failed with status {response.status_code}."
            )
    