from pathlib import Path

from app.api.dependencies import get_gemini_provider
from app.core.exceptions import GeminiSafetyRefusalError
from app.prompts.tryon import TRYON_PROMPT_VERSION
from app.services.gemini_provider import FakeGeminiProvider
from tests.factories import png_bytes


def _upload(client, data: bytes, kind: str) -> str:
    response = client.post(
        "/api/v1/uploads",
        files={"file": (f"{kind}.png", data, "image/png")},
        data={"kind": kind},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


def test_tryon_success(client, storage_root: Path):
    person_id = _upload(client, png_bytes(96, 96), "person")
    jewellery_id = _upload(client, png_bytes(64, 64), "garment")

    response = client.post(
        "/api/v1/try-on",
        json={
            "person_upload_id": person_id,
            "jewellery_upload_id": jewellery_id,
            "category": "necklace",
        },
    )
    assert response.status_code == 201, response.text

    body = response.json()
    assert set(body) == {"data", "meta"}
    data = body["data"]
    assert data["prompt_version"] == TRYON_PROMPT_VERSION
    assert data["content_type"] == "image/png"
    assert data["width"] == 96 and data["height"] == 96
    assert "." not in data["result_id"] and "/" not in data["result_id"]
    assert body["meta"]["request_id"].startswith("req_")
    assert response.headers["x-request-id"] == body["meta"]["request_id"]
    assert (storage_root / "outputs" / "images" / f"{data['result_id']}.png").is_file()


def test_tryon_missing_upload_returns_404(client):
    jewellery_id = _upload(client, png_bytes(48, 48), "garment")
    response = client.post(
        "/api/v1/try-on",
        json={
            "person_upload_id": "0" * 32,
            "jewellery_upload_id": jewellery_id,
            "category": "necklace",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_tryon_invalid_category_returns_422(client):
    person_id = _upload(client, png_bytes(48, 48), "person")
    jewellery_id = _upload(client, png_bytes(48, 48), "garment")
    response = client.post(
        "/api/v1/try-on",
        json={
            "person_upload_id": person_id,
            "jewellery_upload_id": jewellery_id,
            "category": "spaceship",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_tryon_safety_refusal_maps_to_422(client):
    person_id = _upload(client, png_bytes(48, 48), "person")
    jewellery_id = _upload(client, png_bytes(48, 48), "garment")

    previous = client.app.dependency_overrides.get(get_gemini_provider)
    client.app.dependency_overrides[get_gemini_provider] = lambda: FakeGeminiProvider(
        error=GeminiSafetyRefusalError()
    )
    try:
        response = client.post(
            "/api/v1/try-on",
            json={
                "person_upload_id": person_id,
                "jewellery_upload_id": jewellery_id,
                "category": "necklace",
            },
        )
    finally:
        if previous is not None:
            client.app.dependency_overrides[get_gemini_provider] = previous
        else:
            client.app.dependency_overrides.pop(get_gemini_provider, None)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "SAFETY_REFUSED"
    assert response.headers["x-request-id"] == error["request_id"]
