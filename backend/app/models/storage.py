from dataclasses import dataclass
from enum import Enum


class StorageCategory(str, Enum):
    UPLOAD = "upload"
    OUTPUT_IMAGE = "output_image"
    OUTPUT_VIDEO = "output_video"


@dataclass(frozen=True, slots=True)
class StoredObject:
    object_id: str
    key: str
    filename: str
    category: StorageCategory
    size_bytes: int
