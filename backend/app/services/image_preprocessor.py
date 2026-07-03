import io

from PIL import Image, ImageOps

from app.models.gemini import NormalizedImage

_OUTPUT_FORMAT = "PNG"
_OUTPUT_CONTENT_TYPE = "image/png"
_BACKGROUND = (255, 255, 255, 255)


class ImagePreprocessor:
    def __init__(self, max_dimension: int) -> None:
        self._max_dimension = max_dimension

    def normalize(self, data: bytes) -> NormalizedImage:
        with Image.open(io.BytesIO(data)) as image:
            oriented = ImageOps.exif_transpose(image)
            flattened = self._flatten(oriented)
            resized = self._resize(flattened)
            buffer = io.BytesIO()
            resized.save(buffer, format=_OUTPUT_FORMAT)
        return NormalizedImage(
            content=buffer.getvalue(), content_type=_OUTPUT_CONTENT_TYPE
        )

    def _flatten(self, image: Image.Image) -> Image.Image:
        has_alpha = image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        )
        if not has_alpha:
            return image.convert("RGB")
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, _BACKGROUND)
        return Image.alpha_composite(background, rgba).convert("RGB")

    def _resize(self, image: Image.Image) -> Image.Image:
        longest = max(image.size)
        if longest <= self._max_dimension:
            return image
        scale = self._max_dimension / longest
        width = max(1, round(image.width * scale))
        height = max(1, round(image.height * scale))
        return image.resize((width, height), Image.Resampling.LANCZOS)
