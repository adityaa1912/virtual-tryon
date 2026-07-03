import axios from "axios";
import type {
  JewelleryCategory,
  ResponseEnvelope,
  TryOnData,
  UploadData,
  UploadKind,
  VideoData,
} from "./types";

const api = axios.create({ baseURL: "/api/v1" });

export function resultImageUrl(resultId: string): string {
  return `/api/v1/results/${resultId}`;
}

export function videoUrl(videoId: string): string {
  return `/api/v1/videos/${videoId}/content`;
}

export async function uploadImage(
  file: File,
  kind: UploadKind
): Promise<UploadData> {
  const form = new FormData();
  form.append("file", file);
  form.append("kind", kind);
  const { data } = await api.post<ResponseEnvelope<UploadData>>(
    "/uploads",
    form
  );
  return data.data;
}

export async function generateTryOn(
  personUploadId: string,
  jewelleryUploadId: string,
  category: JewelleryCategory
): Promise<TryOnData> {
  const { data } = await api.post<ResponseEnvelope<TryOnData>>("/try-on", {
    person_upload_id: personUploadId,
    jewellery_upload_id: jewelleryUploadId,
    category,
  });
  return data.data;
}

export async function generateVideo(imageResultId: string): Promise<VideoData> {
  const { data } = await api.post<ResponseEnvelope<VideoData>>("/videos", {
    image_result_id: imageResultId,
  });
  return data.data;
}

export function extractErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error) && error.response?.data?.error?.message) {
    return error.response.data.error.message as string;
  }
  return fallback;
}

export async function fetchAsFile(url: string, filename: string): Promise<File> {
  const response = await axios.get(url, { responseType: "blob" });
  const blob = response.data as Blob;
  return new File([blob], filename, { type: blob.type });
}

async function downloadBlob(path: string, filename: string): Promise<void> {
  const response = await api.get(path, { responseType: "blob" });
  const url = URL.createObjectURL(response.data as Blob);
  try {
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  } finally {
    URL.revokeObjectURL(url);
  }
}

export async function downloadResult(resultId: string): Promise<void> {
  await downloadBlob(`/results/${resultId}`, `tryon-${resultId}.png`);
}

export async function downloadVideo(videoId: string): Promise<void> {
  await downloadBlob(`/videos/${videoId}/content`, `tryon-${videoId}.mp4`);
}
