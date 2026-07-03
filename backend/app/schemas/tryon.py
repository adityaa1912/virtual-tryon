from pydantic import BaseModel

from app.models.gemini import JewelleryCategory


class TryOnRequest(BaseModel):
    person_upload_id: str
    jewellery_upload_id: str
    category: JewelleryCategory


class TryOnResponse(BaseModel):
    result_id: str
    prompt_version: str
    model: str
    content_type: str
    width: int
    height: int
    size_bytes: int
