from app.models.gemini import JewelleryCategory

TRYON_PROMPT_VERSION = "tryon-v3"

ROLE = (
    "You are a high-end commercial jewellery retoucher producing a photorealistic "
    "virtual try-on. You receive PERSON IMAGE, a real photograph of a person, and "
    "JEWELLERY IMAGE, a product photograph of one piece of jewellery. Edit ONLY "
    "the PERSON IMAGE so the same person is wearing that exact item, and return a "
    "single editorial-quality photograph."
)

PRESERVE_PERSON = (
    "Keep the person unchanged: the same identity and facial features, skin tone, "
    "hairstyle, expression, pose, body proportions, clothing, camera angle, "
    "framing and background. Preserve the scene lighting exactly, including its "
    "direction, intensity and colour temperature. Keep the original composition "
    "intact, and integrate the jewellery so it looks genuinely photographed on "
    "the person, not pasted on afterwards."
)

PRESERVE_JEWELLERY = (
    "Reproduce the jewellery exactly as shown in the reference: the same scale, "
    "orientation, proportions, metal colour and finish, gemstone colour, texture "
    "and every visible design detail. Never redesign, simplify, or invent missing "
    "parts of it. The jewellery must interact naturally with the body, with "
    "realistic contact shadows, reflections, depth and partial occlusion wherever "
    "appropriate."
)

NEGATIVE = (
    "Do not change the person, skin tone, facial features, pose, clothing or "
    "background. Do not beautify, retouch, or otherwise modify the person's "
    "appearance. Do not add extra jewellery, and do not alter the jewellery's "
    "design."
)

CATEGORY_INSTRUCTIONS: dict[JewelleryCategory, str] = {
    JewelleryCategory.NECKLACE: (
        "Drape the necklace so the chain follows the neck naturally and the "
        "pendant rests in place, with realistic shadows and depth."
    ),
    JewelleryCategory.EARRINGS: (
        "Attach an earring to each visible earlobe at a realistic scale, "
        "preserving the ear shape and hairstyle."
    ),
    JewelleryCategory.RING: (
        "Place the ring on a finger of the visible hand, following the finger's "
        "perspective, with realistic reflections and contact shadows."
    ),
    JewelleryCategory.BRACELET: (
        "Wrap the bracelet around the visible wrist, following the wrist's "
        "curvature, with no floating or clipping."
    ),
    JewelleryCategory.WATCH: (
        "Fasten the watch around the visible wrist following its curvature, with "
        "the dial facing the camera and realistic contact shadows."
    ),
    JewelleryCategory.GLASSES: (
        "Rest the glasses on the face, aligned to the eyes and sitting naturally "
        "on the nose bridge and ears."
    ),
}
