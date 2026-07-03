import io

from PIL import Image

from app.services.image_preprocessor import ImagePreprocessor


def _open(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def _png(width: int, height: int, mode: str = "RGB") -> bytes:
    buffer = io.BytesIO()
    Image.new(mode, (width, height), (10, 120, 200)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_normalize_outputs_rgb_png():
    result = ImagePreprocessor(1536).normalize(_png(64, 64))
    assert result.content_type == "image/png"
    with _open(result.content) as image:
        assert image.format == "PNG"
        assert image.mode == "RGB"


def test_normalize_downscales_oversized_image():
    result = ImagePreprocessor(128).normalize(_png(512, 256))
    with _open(result.content) as image:
        assert image.size == (128, 64)


def test_normalize_does_not_upscale_small_image():
    result = ImagePreprocessor(1024).normalize(_png(100, 80))
    with _open(result.content) as image:
        assert image.size == (100, 80)


def test_normalize_flattens_alpha():
    transparent = io.BytesIO()
    Image.new("RGBA", (40, 40), (0, 0, 0, 0)).save(transparent, format="PNG")
    result = ImagePreprocessor(1536).normalize(transparent.getvalue())
    with _open(result.content) as image:
        assert image.mode == "RGB"


def test_normalize_applies_exif_orientation():
    source = io.BytesIO()
    exif = Image.Exif()
    exif[0x0112] = 6
    Image.new("RGB", (100, 40), (200, 50, 50)).save(
        source, format="JPEG", exif=exif.tobytes()
    )
    result = ImagePreprocessor(1536).normalize(source.getvalue())
    with _open(result.content) as image:
        assert image.size == (40, 100)
