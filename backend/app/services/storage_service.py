import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.exceptions import (
    InvalidStorageKeyError,
    StorageError,
    StorageObjectNotFoundError,
    StorageWriteError,
)
from app.models.storage import StorageCategory, StoredObject
from app.utils.identifiers import new_object_id

_SUBDIR_BY_CATEGORY: dict[StorageCategory, Path] = {
    StorageCategory.UPLOAD: Path("uploads"),
    StorageCategory.OUTPUT_IMAGE: Path("outputs/images"),
    StorageCategory.OUTPUT_VIDEO: Path("outputs/videos"),
}
_TMP_SUBDIR = Path("tmp")


class StorageProvider(ABC):
    @abstractmethod
    def save(
        self, data: bytes, extension: str, category: StorageCategory
    ) -> StoredObject: ...

    @abstractmethod
    def read(self, key: str) -> bytes: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...


class LocalStorageProvider(StorageProvider):
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._tmp_dir = self._root / _TMP_SUBDIR
        self._ensure_layout()

    def save(
        self, data: bytes, extension: str, category: StorageCategory
    ) -> StoredObject:
        object_id = new_object_id()
        filename = f"{object_id}{extension}"
        relative_key = _SUBDIR_BY_CATEGORY[category] / filename
        self._atomic_write(data, self._root / relative_key)
        return StoredObject(
            object_id=object_id,
            key=relative_key.as_posix(),
            filename=filename,
            category=category,
            size_bytes=len(data),
        )

    def read(self, key: str) -> bytes:
        path = self._resolve(key)
        try:
            return path.read_bytes()
        except FileNotFoundError as exc:
            raise StorageObjectNotFoundError(key) from exc
        except OSError as exc:
            raise StorageError(f"Failed to read storage object: {key}.") from exc

    def exists(self, key: str) -> bool:
        return self._resolve(key).is_file()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        try:
            path.unlink()
        except FileNotFoundError as exc:
            raise StorageObjectNotFoundError(key) from exc

    def _ensure_layout(self) -> None:
        self._tmp_dir.mkdir(parents=True, exist_ok=True)
        for subdir in _SUBDIR_BY_CATEGORY.values():
            (self._root / subdir).mkdir(parents=True, exist_ok=True)

    def _atomic_write(self, data: bytes, destination: Path) -> None:
        descriptor, temp_name = tempfile.mkstemp(dir=self._tmp_dir, suffix=".part")
        temp_path = Path(temp_name)
        try:
            with os.fdopen(descriptor, "wb") as temp_file:
                temp_file.write(data)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_path, destination)
        except OSError as exc:
            temp_path.unlink(missing_ok=True)
            raise StorageWriteError(str(destination)) from exc

    def _resolve(self, key: str) -> Path:
        candidate = (self._root / key).resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise InvalidStorageKeyError(key) from exc
        return candidate
