import { useRef, type ChangeEvent } from "react";
import type { SlotStatus } from "../hooks/useImageUpload";
import Spinner from "./Spinner";

interface UploadCardProps {
  title: string;
  hint: string;
  status: SlotStatus;
  previewUrl: string | null;
  error: string | null;
  disabled?: boolean;
  active?: boolean;
  onSelect: (file: File) => void;
  onClear: () => void;
}

export default function UploadCard({
  title,
  hint,
  status,
  previewUrl,
  error,
  disabled = false,
  active,
  onSelect,
  onClear,
}: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const uploading = status === "uploading";

  const openPicker = () => {
    if (!disabled && !uploading) inputRef.current?.click();
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) onSelect(file);
    event.target.value = "";
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-semibold text-slate-700">
          {title}
          {active && (
            <span className="ml-2 rounded-full bg-indigo-100 px-2 py-0.5 text-[10px] font-medium text-indigo-600">
              Active
            </span>
          )}
        </h3>
        {previewUrl && !uploading && !disabled && (
          <button
            type="button"
            onClick={onClear}
            className="text-xs font-medium text-slate-400 transition hover:text-rose-500"
          >
            Remove
          </button>
        )}
      </div>

      <button
        type="button"
        onClick={openPicker}
        disabled={disabled || uploading}
        className="group relative flex aspect-square w-full items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 transition hover:border-indigo-300 hover:bg-indigo-50/40 disabled:cursor-not-allowed"
      >
        {previewUrl ? (
          <img
            src={previewUrl}
            alt={title}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center gap-2 px-6 text-center">
            <span className="flex h-11 w-11 items-center justify-center rounded-full bg-white text-2xl text-indigo-400 shadow-sm">
              +
            </span>
            <span className="text-sm font-medium text-slate-500">{hint}</span>
            <span className="text-xs text-slate-400">PNG, JPG or WEBP</span>
          </div>
        )}

        {uploading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-white/70 text-indigo-600">
            <Spinner className="h-6 w-6" />
            <span className="text-xs font-medium">Uploading…</span>
          </div>
        )}
      </button>

      <p className="min-h-[1rem] text-xs">
        {status === "ready" && (
          <span className="font-medium text-emerald-600">Ready</span>
        )}
        {status === "error" && (
          <span className="font-medium text-rose-600">{error}</span>
        )}
      </p>

      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  );
}
