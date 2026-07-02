from app.models.gemini import JewelleryCategory

TRYON_PROMPT_VERSION = "tryon-v1"

PLACEMENT_BY_CATEGORY: dict[JewelleryCategory, str] = {
    JewelleryCategory.NECKLACE: (
        "Place the necklace naturally around the neck, resting on the skin and "
        "clothing with a correct, gravity-consistent drape."
    ),
    JewelleryCategory.EARRINGS: (
        "Place the earrings on the earlobes, one on each visible ear, matched in "
        "size and orientation."
    ),
    JewelleryCategory.RING: (
        "Place the ring on a finger of the visible hand, sized correctly to the "
        "finger."
    ),
    JewelleryCategory.BRACELET: (
        "Place the bracelet around the visible wrist with a natural, resting fit."
    ),
    JewelleryCategory.WATCH: (
        "Place the watch on the visible wrist, oriented with the dial facing the "
        "camera."
    ),
    JewelleryCategory.GLASSES: (
        "Place the glasses on the face, aligned to the eyes and resting on the "
        "nose bridge and ears."
    ),
}

TRYON_TEMPLATE = """You are an expert photorealistic image editor performing a virtual jewellery try-on. You will receive two images: PERSON IMAGE, a real photograph of a person, and JEWELLERY IMAGE, a product photograph of a single piece of jewellery.

Edit ONLY the PERSON IMAGE so that the same person is naturally wearing the item shown in the JEWELLERY IMAGE. Return exactly one edited photograph and nothing else.

The output must be pixel-faithful to the PERSON IMAGE in every respect except for the added jewellery. Preserve the exact face and identity, the exact skin tone and texture, the hairstyle, the facial expression, the pose and body proportions, the clothing and neckline, the camera angle and framing, the background, and the scene lighting. Keep the result an unretouched-looking real photograph, without illustration, over-smoothing, or beautification.

{placement} Match real-world proportions and scale relative to the person, and render realistic metal and gemstone reflections, contact shadows, and occlusion consistent with the scene lighting.

Do not add any jewellery or accessory that is not present in the JEWELLERY IMAGE. Do not modify, slim, beautify, or reshape the body or face. Do not add text, watermarks, borders, or additional people. Do not change the image dimensions or aspect ratio."""
