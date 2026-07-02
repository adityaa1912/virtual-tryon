class UploadValidationError(Exception):
    status_code: int = 400
    code: str = "VALIDATION_ERROR"
    default_detail: str = "Invalid upload."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class EmptyFileError(UploadValidationError):
    status_code = 400
    code = "EMPTY_FILE"
    default_detail = "Uploaded file is empty."


class FileTooLargeError(UploadValidationError):
    status_code = 413
    code = "PAYLOAD_TOO_LARGE"

    def __init__(self, max_size_bytes: int) -> None:
        super().__init__(
            f"File exceeds the maximum allowed size of {max_size_bytes} bytes."
        )


class UnsupportedMediaTypeError(UploadValidationError):
    status_code = 415
    code = "UNSUPPORTED_MEDIA_TYPE"

    def __init__(self, allowed_mime_types: frozenset[str]) -> None:
        allowed = ", ".join(sorted(allowed_mime_types))
        super().__init__(f"Unsupported file type. Allowed types: {allowed}.")


class CorruptImageError(UploadValidationError):
    status_code = 422
    code = "CORRUPT_IMAGE"
    default_detail = "The uploaded image is corrupt or unreadable."


class ImageDimensionError(UploadValidationError):
    status_code = 413
    code = "IMAGE_DIMENSIONS_EXCEEDED"

    def __init__(self, max_dimension: int) -> None:
        super().__init__(
            f"Image dimensions exceed the maximum of {max_dimension}px per side."
        )


class DecompressionBombError(UploadValidationError):
    status_code = 413
    code = "IMAGE_PIXELS_EXCEEDED"

    def __init__(self, max_pixels: int) -> None:
        super().__init__(
            f"Image exceeds the maximum allowed pixel count of {max_pixels}."
        )


class StorageError(Exception):
    status_code: int = 500
    code: str = "STORAGE_ERROR"

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class StorageWriteError(StorageError):
    status_code = 500
    code = "STORAGE_WRITE_ERROR"

    def __init__(self, destination: str) -> None:
        super().__init__(f"Failed to write storage object at {destination}.")


class StorageObjectNotFoundError(StorageError):
    status_code = 404
    code = "NOT_FOUND"

    def __init__(self, key: str) -> None:
        super().__init__(f"Storage object not found: {key}.")


class InvalidStorageKeyError(StorageError):
    status_code = 400
    code = "INVALID_STORAGE_KEY"

    def __init__(self, key: str) -> None:
        super().__init__(f"Invalid storage key: {key}.")


class GeminiError(Exception):
    status_code: int = 502
    code: str = "UPSTREAM_ERROR"
    default_detail: str = "The image generation service failed."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class GeminiServerError(GeminiError):
    status_code = 502
    code = "UPSTREAM_ERROR"
    default_detail = "The image generation service returned a server error."


class GeminiTimeoutError(GeminiError):
    status_code = 504
    code = "UPSTREAM_TIMEOUT"
    default_detail = "The image generation service timed out."


class GeminiRateLimitError(GeminiError):
    status_code = 429
    code = "RATE_LIMITED"
    default_detail = "The image generation service is rate limited."


class GeminiSafetyRefusalError(GeminiError):
    status_code = 422
    code = "SAFETY_REFUSED"
    default_detail = "The request was refused by the image generation safety filters."


class GeminiEmptyResponseError(GeminiError):
    status_code = 502
    code = "EMPTY_GENERATION"
    default_detail = "The image generation service returned no image."


class GeminiInvalidOutputError(GeminiError):
    status_code = 502
    code = "INVALID_GENERATION"
    default_detail = "The image generation service returned an invalid image."
