from pydantic import BaseModel


class VideoRequest(BaseModel):
    image_result_id: str


class VideoResponse(BaseModel):
    video_id: str
