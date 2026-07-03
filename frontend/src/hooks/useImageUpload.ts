import { useCallback, useEffect, useRef, useState } from "react";
import { extractErrorMessage, fetchAsFile, uploadImage } from "../api/client";
import type { UploadKind } from "../api/types";

export type SlotStatus = "empty" | "uploading" | "ready" | "error";

export interface ImageSlot {
  file: File | null;
  previewUrl: string | null;
  uploadId: string | null;
  status: SlotStatus;
  error: string | null;
  select: (file: File) => void;
  selectRemote: (url: string, filename: string) => void;
  clear: () => void;
}

export function useImageUpload(kind: UploadKind): ImageSlot {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);
  const [status, setStatus] = useState<SlotStatus>("empty");
  const [error, setError] = useState<string | null>(null);
  const requestToken = useRef(0);

  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const runUpload = useCallback(
    (token: number, nextFile: File) => {
      setFile(nextFile);
      setUploadId(null);
      setError(null);
      setStatus("uploading");
      uploadImage(nextFile, kind)
        .then((data) => {
          if (requestToken.current !== token) return;
          setUploadId(data.id);
          setStatus("ready");
        })
        .catch((err) => {
          if (requestToken.current !== token) return;
          setError(extractErrorMessage(err, "Upload failed. Please try again."));
          setStatus("error");
        });
    },
    [kind]
  );

  const select = useCallback(
    (nextFile: File) => {
      runUpload(++requestToken.current, nextFile);
    },
    [runUpload]
  );

  const selectRemote = useCallback(
    (url: string, filename: string) => {
      const token = ++requestToken.current;
      setFile(null);
      setUploadId(null);
      setError(null);
      setStatus("uploading");
      fetchAsFile(url, filename)
        .then((nextFile) => {
          if (requestToken.current !== token) return;
          runUpload(token, nextFile);
        })
        .catch((err) => {
          if (requestToken.current !== token) return;
          setError(extractErrorMessage(err, "Could not load the item."));
          setStatus("error");
        });
    },
    [runUpload]
  );

  const clear = useCallback(() => {
    requestToken.current += 1;
    setFile(null);
    setPreviewUrl(null);
    setUploadId(null);
    setError(null);
    setStatus("empty");
  }, []);

  return {
    file,
    previewUrl,
    uploadId,
    status,
    error,
    select,
    selectRemote,
    clear,
  };
}
