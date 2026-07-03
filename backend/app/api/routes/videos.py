from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_video_service
from app.schemas.common import ResponseEnvelope, ResponseMeta
from app.schemas.video import VideoRequest, VideoResponse
from app.services.video_service import VideoService

router = APIRouter(tags=["Videos"])


@router.post(
    "/videos",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseEnvelope[VideoResponse],
)
async def create_video(
    request: Request,
    payload: VideoRequest,
    service: VideoService = Depends(get_video_service),
) -> ResponseEnvelope[VideoResponse]:
    video_id = await service.create(payload.image_result_id)
    return ResponseEnvelope[VideoResponse](
        data=VideoResponse(video_id=video_id),
        meta=ResponseMeta(request_id=request.state.request_id),
    )
