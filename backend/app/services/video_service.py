from dataclasses import dataclass

from anyio import to_thread

from app.core.exceptions import ResultNotFoundError
from app.models.storage import StorageCategory
from app.services.storage_service import StorageProvider
from app.services.video_provider import VideoProvider


@dataclass(frozen=True, slots=True)
class _LoadedImage:
    content: bytes
    content_type: str


class VideoService:
    def __init__(self, storage: StorageProvider, provider: VideoProvider) -> None:
        self._storage = storage
        self._provider = provider

    async def create(self, image_result_id: str) -> str:
        image = await to_thread.run_sync(self._load_image, image_result_id)
        video = await self._provider.generate(image.content, image.content_type)
        return await to_thread.run_sync(self._store_video, video.content)

    def _load_image(self, image_result_id: str) -> _LoadedImage:
        stored = self._storage.find(image_result_id, StorageCategory.OUTPUT_IMAGE)
        if stored is None:
            raise ResultNotFoundError(image_result_id)
        data = self._storage.read(stored.key)
        content_type = "image/png" if stored.filename.endswith(".png") else "image/jpeg"
        return _LoadedImage(content=data, content_type=content_type)

    def _store_video(self, content: bytes) -> str:
        stored = self._storage.save(content, ".mp4", StorageCategory.OUTPUT_VIDEO)
        return stored.object_id
