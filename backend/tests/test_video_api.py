from tests.factories import png_bytes


def _upload(client, data: bytes, kind: str) -> str:
    response = client.post(
        "/api/v1/uploads",
        files={"file": (f"{kind}.png", data, "image/png")},
        data={"kind": kind},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


def _create_image_result(client) -> str:
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


def test_video_generation_and_download(client):
    result_id = _create_image_result(client)

    create = client.post("/api/v1/videos", json={"image_result_id": result_id})
    assert create.status_code == 201, create.text
    video_id = create.json()["data"]["video_id"]
    assert "." not in video_id and "/" not in video_id

    content = client.get(f"/api/v1/videos/{video_id}/content")
    assert content.status_code == 200
    assert content.headers["content-type"] == "video/mp4"
    assert len(content.content) > 0


def test_video_generation_missing_image_returns_404(client):
    response = client.post("/api/v1/videos", json={"image_result_id": "0" * 32})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
