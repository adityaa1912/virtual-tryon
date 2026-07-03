from dataclasses import dataclass

from app.models.gemini import TryOnResult


@dataclass(frozen=True, slots=True)
class TryOnOutcome:
    result_id: str
    result: TryOnResult
