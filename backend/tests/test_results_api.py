from tests.factories import png_bytes


def _upload(client, data: bytes, kind: str) -> str:
    response = client.post(
        "/api/v1/uploads",
        files={"file": (f"{kind}.png", data, "image/png")},
        data={"kind": kind},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


def _create_result(client) -> str:
    person_id = _upload(client, png_bytes(64, 64), "person")
    jewellery_id = _upload(client, png_bytes(48, 48), "garment")
    response = client.post(
        "/api/v1/try-on",
        json={
            "person_upload_id": person_id,
            "jewellery_upload_id": jewellery_id,
            "category": "necklace",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["result_id"]


def test_get_result_returns_image(client):
    result_id = _create_result(client)
    response = client.get(f"/api/v1/results/{result_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_get_missing_result_returns_404(client):
    response = client.get(f"/api/v1/results/{'0' * 32}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_result_rejects_malformed_id(client):
    response = client.get("/api/v1/results/not-a-valid-id")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_STORAGE_KEY"
