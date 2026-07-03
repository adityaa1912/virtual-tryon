import pytest

from app.core.exceptions import InvalidStorageKeyError, StorageObjectNotFoundError
from app.models.storage import StorageCategory
from app.services.storage_service import LocalStorageProvider
from tests.factories import png_bytes


@pytest.fixture
def provider(tmp_path) -> LocalStorageProvider:
    return LocalStorageProvider(tmp_path)


def test_creates_directory_layout(provider, tmp_path):
    for subdir in ("uploads", "outputs/images", "outputs/videos", "tmp"):
        assert (tmp_path / subdir).is_dir()


def test_saves_across_categories(provider, tmp_path):
    upload = provider.save(png_bytes(), ".png", StorageCategory.UPLOAD)
    image = provider.save(b"\x00result", ".png", StorageCategory.OUTPUT_IMAGE)
    video = provider.save(b"\x00video", ".mp4", StorageCategory.OUTPUT_VIDEO)

    assert upload.key.startswith("uploads/") and upload.key.endswith(".png")
    assert image.key.startswith("outputs/images/")
    assert video.key.startswith("outputs/videos/") and video.key.endswith(".mp4")
    assert (tmp_path / upload.key).is_file()
    assert upload.filename == f"{upload.object_id}.png"


def test_read_round_trip(provider):
    data = png_bytes()
    stored = provider.save(data, ".png", StorageCategory.UPLOAD)
    assert provider.read(stored.key) == data


def test_exists(provider):
    stored = provider.save(png_bytes(), ".png", StorageCategory.UPLOAD)
    assert provider.exists(stored.key) is True
    assert provider.exists("uploads/missing.png") is False


def test_no_temp_leftovers(provider, tmp_path):
    provider.save(png_bytes(), ".png", StorageCategory.UPLOAD)
    assert list((tmp_path / "tmp").iterdir()) == []


def test_rejects_path_traversal(provider):
    with pytest.raises(InvalidStorageKeyError):
        provider.read("../../../etc/passwd")


def test_read_missing_object(provider):
    with pytest.raises(StorageObjectNotFoundError):
        provider.read("uploads/does-not-exist.png")


def test_delete(provider):
    stored = provider.save(png_bytes(), ".png", StorageCategory.UPLOAD)
    provider.delete(stored.key)
    assert provider.exists(stored.key) is False
    with pytest.raises(StorageObjectNotFoundError):
        provider.read(stored.key)


def test_find_locates_object_by_id(provider):
    stored = provider.save(png_bytes(), ".png", StorageCategory.UPLOAD)
    found = provider.find(stored.object_id, StorageCategory.UPLOAD)
    assert found is not None
    assert found.object_id == stored.object_id
    assert found.key == stored.key
    assert provider.read(found.key) == provider.read(stored.key)


def test_find_returns_none_for_absent_id(provider):
    assert provider.find("0" * 32, StorageCategory.UPLOAD) is None


def test_find_rejects_malformed_id(provider):
    with pytest.raises(InvalidStorageKeyError):
        provider.find("../../../etc/passwd", StorageCategory.UPLOAD)
