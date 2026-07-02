from pathlib import Path

from tests.factories import png_bytes


def test_upload_success(client, storage_root: Path):
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("client.png", png_bytes(80, 60), "image/png")},
        data={"kind": "person"},
    )
    assert response.status_code == 201, response.text

    body = response.json()
    assert set(body) == {"data", "meta"}

    data = body["data"]
    assert data["kind"] == "person"
    assert data["content_type"] == "image/png"
    assert data["width"] == 80 and data["height"] == 60
    assert len(data["sha256"]) == 64
    assert "." not in data["id"] and "/" not in data["id"]
    assert {"filename", "key", "extension"}.isdisjoint(data)

    assert body["meta"]["request_id"].startswith("req_")
    assert response.headers["x-request-id"] == body["meta"]["request_id"]
    assert (storage_root / "uploads" / f"{data['id']}.png").is_file()


def test_upload_rejects_spoofed_type(client):
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("evil.png", b"not an image", "image/png")},
    )
    assert response.status_code == 415
    error = response.json()["error"]
    assert error["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert error["request_id"].startswith("req_")
    assert response.headers["x-request-id"] == error["request_id"]


def test_upload_missing_file_returns_validation_error(client):
    response = client.post("/api/v1/uploads", data={"kind": "person"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert any(detail["field"].endswith("file") for detail in error["details"])


def test_upload_rejects_invalid_kind(client):
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("a.png", png_bytes(32, 32), "image/png")},
        data={"kind": "hat"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_request_id_is_echoed_when_supplied(client):
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("a.png", png_bytes(16, 16), "image/png")},
        headers={"X-Request-ID": "req_supplied"},
    )
    assert response.status_code == 201
    assert response.json()["meta"]["request_id"] == "req_supplied"
    assert response.headers["x-request-id"] == "req_supplied"


def test_health_is_unversioned_and_flat(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "running", "service": "virtual-tryon-api"}
    assert response.headers["x-request-id"].startswith("req_")


def test_openapi_documents_upload(client):
    schema = client.get("/openapi.json").json()
    assert "/api/v1/uploads" in schema["paths"]
    operation = schema["paths"]["/api/v1/uploads"]["post"]
    assert "201" in operation["responses"]
    assert "Uploads" in operation["tags"]
