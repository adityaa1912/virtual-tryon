import io

from PIL import Image


def png_bytes(width: int = 64, height: int = 64) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (200, 120, 40)).save(buffer, format="PNG")
    return buffer.getvalue()


def jpeg_bytes(width: int = 64, height: int = 64) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (10, 200, 90)).save(buffer, format="JPEG")
    return buffer.getvalue()
