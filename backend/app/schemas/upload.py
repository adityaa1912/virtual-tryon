from enum import Enum

from pydantic import BaseModel


class UploadKind(str, Enum):
    PERSON = "person"
    GARMENT = "garment"


class UploadResponse(BaseModel):
    id: str
    kind: UploadKind | None = None
    content_type: str
    size_bytes: int
    width: int
    height: int
    sha256: str
