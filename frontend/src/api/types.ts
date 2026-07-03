export const JEWELLERY_CATEGORIES = [
  "necklace",
  "earrings",
  "ring",
  "bracelet",
  "watch",
  "glasses",
] as const;

export type JewelleryCategory = (typeof JEWELLERY_CATEGORIES)[number];

export type UploadKind = "person" | "garment";

export interface ResponseMeta {
  request_id: string;
}

export interface ResponseEnvelope<T> {
  data: T;
  meta: ResponseMeta;
}

export interface UploadData {
  id: string;
  kind: UploadKind | null;
  content_type: string;
  size_bytes: number;
  width: number;
  height: number;
  sha256: string;
}

export interface TryOnData {
  result_id: string;
  prompt_version: string;
  model: string;
  content_type: string;
  width: number;
  height: number;
  size_bytes: number;
}

export interface VideoData {
  video_id: string;
}
