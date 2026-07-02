from app.models.gemini import BuiltPrompt, JewelleryCategory
from app.prompts.tryon import (
    PLACEMENT_BY_CATEGORY,
    TRYON_PROMPT_VERSION,
    TRYON_TEMPLATE,
)


class PromptBuilder:
    def build_tryon(self, category: JewelleryCategory) -> BuiltPrompt:
        placement = PLACEMENT_BY_CATEGORY[category]
        text = TRYON_TEMPLATE.format(placement=placement)
        return BuiltPrompt(text=text, version=TRYON_PROMPT_VERSION)
