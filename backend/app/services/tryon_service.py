from anyio import to_thread

from app.core.exceptions import UploadNotFoundError
from app.models.gemini import JewelleryCategory, NormalizedImage, TryOnResult
from app.models.storage import StorageCategory
from app.models.tryon import TryOnOutcome
from app.services.gemini_service import GeminiService
from app.services.image_preprocessor import ImagePreprocessor
from app.services.storage_service import StorageProvider


class TryOnService:
    def __init__(
        self,
        storage: StorageProvider,
        preprocessor: ImagePreprocessor,
        gemini_service: GeminiService,
    ) -> None:
        self._storage = storage
        self._preprocessor = preprocessor
        self._gemini_service = gemini_service

    async def create(
        self,
        person_upload_id: str,
        jewellery_upload_id: str,
        category: JewelleryCategory,
    ) -> TryOnOutcome:
        person, jewellery = await to_thread.run_sync(
            self._prepare_inputs, person_upload_id, jewellery_upload_id
        )
        result = await self._gemini_service.generate_tryon(person, jewellery, category)
        result_id = await to_thread.run_sync(self._store_result, result)
        return TryOnOutcome(result_id=result_id, result=result)

    def _prepare_inputs(
        self, person_upload_id: str, jewellery_upload_id: str
    ) -> tuple[NormalizedImage, NormalizedImage]:
        person = self._load_and_normalize(person_upload_id)
        jewellery = self._load_and_normalize(jewellery_upload_id)
        return person, jewellery

    def _load_and_normalize(self, upload_id: str) -> NormalizedImage:
        stored = self._storage.find(upload_id, StorageCategory.UPLOAD)
        if stored is None:
            raise UploadNotFoundError(upload_id)
        data = self._storage.read(stored.key)
        return self._preprocessor.normalize(data)

    def _store_result(self, result: TryOnResult) -> str:
        stored = self._storage.save(
            result.image.content,
            result.image.extension,
            StorageCategory.OUTPUT_IMAGE,
        )
        return stored.object_id
