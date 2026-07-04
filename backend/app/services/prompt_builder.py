from app.models.gemini import BuiltPrompt, JewelleryCategory
from app.prompts.tryon import (
    CATEGORY_INSTRUCTIONS,
    NEGATIVE,
    PRESERVE_JEWELLERY,
    PRESERVE_PERSON,
    ROLE,
    TRYON_PROMPT_VERSION,
)

_SHARED_INTRO = "\n\n".join([ROLE, PRESERVE_PERSON, PRESERVE_JEWELLERY])


class PromptBuilder:
    def build_tryon(self, category: JewelleryCategory) -> BuiltPrompt:
        text = "\n\n".join(
            [_SHARED_INTRO, CATEGORY_INSTRUCTIONS[category], NEGATIVE]
        )
        return BuiltPrompt(text=text, version=TRYON_PROMPT_VERSION)
