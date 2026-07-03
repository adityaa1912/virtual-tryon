import type { JewelleryCategory } from "../api/types";

export interface CatalogueItem {
  id: string;
  name: string;
  category: JewelleryCategory;
  imageUrl: string;
}

export const CATALOGUE: CatalogueItem[] = [
  {
    id: "gold-necklace",
    name: "Gold Necklace",
    category: "necklace",
    imageUrl: "/jewellery/gold-necklace.png",
  },
  {
    id: "pearl-earrings",
    name: "Pearl Earrings",
    category: "earrings",
    imageUrl: "/jewellery/pearl-earrings.png",
  },
  {
    id: "diamond-ring",
    name: "Diamond Ring",
    category: "ring",
    imageUrl: "/jewellery/diamond-ring.png",
  },
  {
    id: "silver-bracelet",
    name: "Silver Bracelet",
    category: "bracelet",
    imageUrl: "/jewellery/silver-bracelet.png",
  },
  {
    id: "classic-watch",
    name: "Classic Watch",
    category: "watch",
    imageUrl: "/jewellery/classic-watch.png",
  },
  {
    id: "round-glasses",
    name: "Round Glasses",
    category: "glasses",
    imageUrl: "/jewellery/round-glasses.png",
  },
];
