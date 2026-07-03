import mimetypes

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.api.dependencies import get_storage_provider
from app.core.exceptions import StorageObjectNotFoundError
from app.models.storage import StorageCategory
from app.services.storage_service import StorageProvider

router = APIRouter(tags=["Results"])


@router.get("/results/{result_id}")
def get_result(
    result_id: str,
    storage: StorageProvider = Depends(get_storage_provider),
) -> Response:
    stored = storage.find(result_id, StorageCategory.OUTPUT_IMAGE)
    if stored is None:
        raise StorageObjectNotFoundError(result_id)
    data = storage.read(stored.key)
    media_type = mimetypes.guess_type(stored.filename)[0] or "application/octet-stream"
    return Response(content=data, media_type=media_type)


@router.get("/videos/{video_id}/content")
def get_video(
    video_id: str,
    storage: StorageProvider = Depends(get_storage_provider),
) -> Response:
    stored = storage.find(video_id, StorageCategory.OUTPUT_VIDEO)
    if stored is None:
        raise StorageObjectNotFoundError(video_id)
    data = storage.read(stored.key)
    media_type = mimetypes.guess_type(stored.filename)[0] or "application/octet-stream"
    return Response(content=data, media_type=media_type)
