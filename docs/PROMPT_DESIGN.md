# Gemini Prompt Design

The try-on prompt is versioned (`tryon-v3`) and assembled by `PromptBuilder`
from reusable fragments plus one category-specific instruction, so shared rules
live in exactly one place and each prompt stays short.

- **Identity preservation.** The prompt instructs Gemini to edit *only* the
  person image and keep the same identity, facial features, skin tone,
  hairstyle, expression, pose, body proportions and clothing — and explicitly
  forbids beautifying or retouching. Image models drift on faces and lighten
  skin by default, so these constraints protect the actual user.
- **Lighting & scene preservation.** It preserves the camera angle, framing,
  background and the scene lighting's direction, intensity and colour
  temperature. Matching the existing light is the single biggest lever for a
  result that looks photographed rather than pasted.
- **Jewellery fidelity.** It requires reproducing the reference exactly — scale,
  orientation, proportions, metal colour and finish, gemstone colour, texture
  and every visible design detail — and never redesigning, simplifying or
  inventing missing parts. A short category clause adds correct placement and
  physics (e.g. chain follows the neck; ring follows finger perspective with
  contact shadows), and one sentence asks for realistic contact shadows,
  reflections, depth and partial occlusion.
- **Why the constraints exist.** Generative editors optimise for plausibility,
  not fidelity; without explicit guardrails they "improve" the person and
  reinterpret the product. A negative section restates the hard prohibitions
  where models weight instructions most.
- **Why prompt engineering matters here.** It is the primary quality lever:
  paired with low temperature and a single candidate, precise constraints turn a
  creative model into a faithful editor, and generated output is re-validated as
  a real image before it is stored. Versioning every prompt keeps each
  generation traceable to the exact instruction that produced it.
