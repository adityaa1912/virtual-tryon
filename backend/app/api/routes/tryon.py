from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_tryon_service
from app.schemas.common import ResponseEnvelope, ResponseMeta
from app.schemas.tryon import TryOnRequest, TryOnResponse
from app.services.tryon_service import TryOnService

router = APIRouter(tags=["Try-On"])


@router.post(
    "/try-on",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[TryOnResponse],
)
async def create_tryon(
    request: Request,
    payload: TryOnRequest,
    service: TryOnService = Depends(get_tryon_service),
) -> ResponseEnvelope[TryOnResponse]:
    outcome = await service.create(
        payload.person_upload_id, payload.jewellery_upload_id, payload.category
    )
    result = outcome.result
    data = TryOnResponse(
        result_id=outcome.result_id,
        prompt_version=result.prompt_version,
        model=result.model,
        content_type=result.image.content_type,
        width=result.image.width,
        height=result.image.height,
        size_bytes=result.image.size_bytes,
    )
    return ResponseEnvelope[TryOnResponse](
        data=data, meta=ResponseMeta(request_id=request.state.request_id)
    )
