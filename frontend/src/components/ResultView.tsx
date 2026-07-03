import { resultImageUrl, videoUrl } from "../api/client";
import type { TryOnData, VideoData } from "../api/types";
import Spinner from "./Spinner";

interface ResultViewProps {
  originalUrl: string;
  result: TryOnData;
  downloading: boolean;
  downloadError: string | null;
  video: VideoData | null;
  generatingVideo: boolean;
  videoError: string | null;
  downloadingVideo: boolean;
  onDownload: () => void;
  onGenerateVideo: () => void;
  onDownloadVideo: () => void;
  onReset: () => void;
}

export default function ResultView({
  originalUrl,
  result,
  downloading,
  downloadError,
  video,
  generatingVideo,
  videoError,
  downloadingVideo,
  onDownload,
  onGenerateVideo,
  onDownloadVideo,
  onReset,
}: ResultViewProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <figure className="flex flex-col gap-2">
          <img
            src={originalUrl}
            alt="Original"
            className="aspect-square w-full rounded-2xl object-cover ring-1 ring-slate-200"
          />
          <figcaption className="text-center text-xs font-medium uppercase tracking-wide text-slate-400">
            Original
          </figcaption>
        </figure>
        <figure className="flex flex-col gap-2">
          <img
            src={resultImageUrl(result.result_id)}
            alt="Generated try-on"
            className="aspect-square w-full rounded-2xl object-cover ring-2 ring-indigo-300"
          />
          <figcaption className="text-center text-xs font-medium uppercase tracking-wide text-indigo-400">
            Try-On Result
          </figcaption>
        </figure>
      </div>

      {downloadError && (
        <p className="text-center text-sm font-medium text-rose-600">
          {downloadError}
        </p>
      )}

      <div className="flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onDownload}
          disabled={downloading}
          className="flex-1 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-60"
        >
          {downloading ? "Preparing download…" : "Download image"}
        </button>
        <button
          type="button"
          onClick={onReset}
          className="flex-1 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50"
        >
          Start over
        </button>
      </div>

      <div className="flex flex-col gap-3 border-t border-slate-100 pt-6">
        {video ? (
          <>
            <video
              src={videoUrl(video.video_id)}
              controls
              autoPlay
              loop
              muted
              playsInline
              className="w-full rounded-2xl bg-black ring-1 ring-slate-200"
            />
            <button
              type="button"
              onClick={onDownloadVideo}
              disabled={downloadingVideo}
              className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 disabled:opacity-60"
            >
              {downloadingVideo ? "Preparing download…" : "Download video"}
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={onGenerateVideo}
            disabled={generatingVideo}
            className="flex items-center justify-center gap-2 rounded-xl bg-slate-800 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-900 disabled:opacity-60"
          >
            {generatingVideo ? (
              <>
                <Spinner /> Generating video…
              </>
            ) : (
              "Generate video"
            )}
          </button>
        )}

        {videoError && (
          <p className="text-center text-sm font-medium text-rose-600">
            {videoError}
          </p>
        )}
      </div>
    </div>
  );
}
