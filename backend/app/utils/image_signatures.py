MIME_JPEG = "image/jpeg"
MIME_PNG = "image/png"
MIME_WEBP = "image/webp"

EXTENSION_BY_MIME: dict[str, str] = {
    MIME_JPEG: ".jpg",
    MIME_PNG: ".png",
    MIME_WEBP: ".webp",
}


def sniff_mime_type(header: bytes) -> str | None:
    if header.startswith(b"\xff\xd8\xff"):
        return MIME_JPEG
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return MIME_PNG
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return MIME_WEBP
    return None
