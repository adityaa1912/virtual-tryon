from app.models.gemini import JewelleryCategory
from app.prompts.tryon import TRYON_PROMPT_VERSION
from app.services.prompt_builder import PromptBuilder


def test_build_tryon_carries_version_and_preservation_clauses():
    prompt = PromptBuilder().build_tryon(JewelleryCategory.NECKLACE)
    assert prompt.version == TRYON_PROMPT_VERSION

    lowered = prompt.text.lower()
    for clause in ("identity", "skin tone", "background", "lighting", "proportions"):
        assert clause in lowered
    assert "necklace" in lowered


def test_build_tryon_varies_placement_by_category():
    builder = PromptBuilder()
    necklace = builder.build_tryon(JewelleryCategory.NECKLACE)
    ring = builder.build_tryon(JewelleryCategory.RING)

    assert necklace.text != ring.text
    assert "necklace" in necklace.text.lower()
    assert "finger" in ring.text.lower()
