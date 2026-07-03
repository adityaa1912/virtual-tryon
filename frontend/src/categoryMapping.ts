import type { JewelleryCategory } from "./api/types";

export type BodyPart = "face" | "hand";

export const BODY_PART_BY_CATEGORY: Record<JewelleryCategory, BodyPart> = {
  necklace: "face",
  earrings: "face",
  glasses: "face",
  ring: "hand",
  bracelet: "hand",
  watch: "hand",
};
