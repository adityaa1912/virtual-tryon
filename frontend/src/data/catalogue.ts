import type { JewelleryCategory } from "../api/types";

export interface CatalogueItem {
  id: string;
  name: string;
  category: JewelleryCategory;
  imageUrl: string;
}

export const CATALOGUE: CatalogueItem[] = [
  {
    id: "gold-heart-necklace",
    name: "Gold Heart Necklace",
    category: "necklace",
    imageUrl: "/jewellery/gold-heart-necklace.png",
  },
  {
    id: "diamond-pendant-necklace",
    name: "Diamond Pendant Necklace",
    category: "necklace",
    imageUrl: "/jewellery/diamond-pendant-necklace.png",
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
];
