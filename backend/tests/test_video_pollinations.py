import asyncio

import httpx
import pytest

from app.core.exceptions import VideoError, VideoRateLimitError, VideoTimeoutError
from app.services.video_pollinations import PollinationsVideoProvider

_PNG = b"\x89PNG\r\n\x1a\n"


def make_provider(handler) -> PollinationsVideoProvider:
    return PollinationsVideoProvider(
        api_key="sk_test",
        base_url="https://gen.example",
        media_url="https://media.example",
        model="wan",
        duration=5,
        aspect_ratio="1:1",
        timeout_seconds=30.0,
        transport=httpx.MockTransport(handler),
    )


def run(provider: PollinationsVideoProvider):
    return asyncio.run(provider.generate(_PNG, "image/png"))


def _video_response() -> httpx.Response:
    return httpx.Response(200, content=b"MP4DATA", headers={"content-type": "video/mp4"})


def test_generate_success():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/upload":
            return httpx.Response(200, json={"url": "https://media.example/abc"})
        return _video_response()

    result = run(make_provider(handler))
    assert result.content == b"MP4DATA"
    assert result.content_type == "video/mp4"


def test_upload_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": {"message": "upload boom"}})

    with pytest.raises(VideoError):
        run(make_provider(handler))


def test_invalid_credentials():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "invalid key"}})

    with pytest.raises(VideoError):
        run(make_provider(handler))


def test_api_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/upload":
            return httpx.Response(200, json={"url": "https://media.example/abc"})
        return httpx.Response(400, json={"error": {"message": "bad request"}})

    with pytest.raises(VideoError):
        run(make_provider(handler))


def test_rate_limited():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "slow down"}})

    with pytest.raises(VideoRateLimitError):
        run(make_provider(handler))


def test_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(VideoTimeoutError):
        run(make_provider(handler))


def test_invalid_video_response():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/upload":
            return httpx.Response(200, json={"url": "https://media.example/abc"})
        return httpx.Response(200, json={"error": {"message": "no video"}})

    with pytest.raises(VideoError):
        run(make_provider(handler))


def test_upload_missing_url():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "field"})

    with pytest.raises(VideoError):
        run(make_provider(handler))


def test_network_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route", request=request)

    with pytest.raises(VideoError):
        run(make_provider(handler))
