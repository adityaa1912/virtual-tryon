from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.concurrency import run_in_threadpool

from app.api.dependencies import get_storage_provider, validate_image_upload
from app.models.storage import StorageCategory
from app.models.upload import ValidatedImage
from app.schemas.common import ResponseEnvelope, ResponseMeta
from app.schemas.upload import UploadKind, UploadResponse
from app.services.storage_service import StorageProvider

router = APIRouter(tags=["Uploads"])


@router.post(
    "/uploads",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[UploadResponse],
)
async def create_upload(
    request: Request,
    kind: UploadKind | None = Form(default=None),
    validated: ValidatedImage = Depends(validate_image_upload),
    storage: StorageProvider = Depends(get_storage_provider),
) -> ResponseEnvelope[UploadResponse]:
    stored = await run_in_threadpool(
        storage.save, validated.content, validated.extension, StorageCategory.UPLOAD
    )
    data = UploadResponse(
        id=stored.object_id,
        kind=kind,
        content_type=validated.content_type,
        size_bytes=validated.size_bytes,
        width=validated.width,
        height=validated.height,
        sha256=validated.sha256,
    )
    return ResponseEnvelope[UploadResponse](
        data=data, meta=ResponseMeta(request_id=request.state.request_id)
    )
