import hashlib
import io

from PIL import Image


def open_image_dimensions(data: bytes) -> tuple[int, int]:
    with Image.open(io.BytesIO(data)) as image:
        return image.width, image.height


def verify_image_integrity(data: bytes) -> None:
    with Image.open(io.BytesIO(data)) as image:
        image.verify()


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
