from app.core.exceptions import GeminiInvalidOutputError, UploadValidationError
from app.models.gemini import (
    GeneratedImage,
    GeminiImagePart,
    GeminiRequest,
    GenerationConfig,
    JewelleryCategory,
    NormalizedImage,
    TryOnResult,
)
from app.models.upload import ValidatedImage
from app.services.gemini_provider import GeminiProvider
from app.services.prompt_builder import PromptBuilder
from app.services.validation_service import ImageValidator

_PERSON_LABEL = "PERSON IMAGE"
_JEWELLERY_LABEL = "JEWELLERY IMAGE"


class GeminiService:
    def __init__(
        self,
        provider: GeminiProvider,
        prompt_builder: PromptBuilder,
        generation_config: GenerationConfig,
        output_validator: ImageValidator,
    ) -> None:
        self._provider = provider
        self._prompt_builder = prompt_builder
        self._config = generation_config
        self._output_validator = output_validator

    async def generate_tryon(
        self,
        person_image: NormalizedImage,
        jewellery_image: NormalizedImage,
        category: JewelleryCategory,
    ) -> TryOnResult:
        prompt = self._prompt_builder.build_tryon(category)
        request = GeminiRequest(
            parts=(
                GeminiImagePart(label=_PERSON_LABEL, image=person_image),
                GeminiImagePart(label=_JEWELLERY_LABEL, image=jewellery_image),
            ),
            prompt_text=prompt.text,
            config=self._config,
        )
        generated = await self._provider.generate(request)
        validated = self._validate_output(generated)
        return TryOnResult(
            image=validated,
            prompt_version=prompt.version,
            model=self._config.model,
        )

    def _validate_output(self, generated: GeneratedImage) -> ValidatedImage:
        try:
            return self._output_validator.validate_bytes(generated.content)
        except UploadValidationError as exc:
            raise GeminiInvalidOutputError() from exc
