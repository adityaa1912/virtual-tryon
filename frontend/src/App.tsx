import { useState } from "react";
import {
  downloadResult,
  downloadVideo,
  extractErrorMessage,
  generateTryOn,
  generateVideo,
} from "./api/client";
import type { JewelleryCategory, TryOnData, VideoData } from "./api/types";
import CatalogueGrid from "./components/CatalogueGrid";
import CategorySelector from "./components/CategorySelector";
import ErrorBanner from "./components/ErrorBanner";
import HealthBadge from "./components/HealthBadge";
import ResultView from "./components/ResultView";
import Spinner from "./components/Spinner";
import UploadCard from "./components/UploadCard";
import { BODY_PART_BY_CATEGORY } from "./categoryMapping";
import { CATALOGUE } from "./data/catalogue";
import { useImageUpload } from "./hooks/useImageUpload";

export default function App() {
  const face = useImageUpload("person");
  const hand = useImageUpload("person");
  const jewellery = useImageUpload("garment");
  const [category, setCategory] = useState<JewelleryCategory>("necklace");
  const [catalogueId, setCatalogueId] = useState<string | null>(null);
  const [cataloguePreview, setCataloguePreview] = useState<string | null>(null);

  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [result, setResult] = useState<TryOnData | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const [video, setVideo] = useState<VideoData | null>(null);
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [downloadingVideo, setDownloadingVideo] = useState(false);

  const bodyPart = BODY_PART_BY_CATEGORY[category];
  const person = bodyPart === "face" ? face : hand;

  const canGenerate =
    person.status === "ready" && jewellery.status === "ready" && !generating;

  const selectCatalogueItem = (itemId: string) => {
    const item = CATALOGUE.find((entry) => entry.id === itemId);
    if (!item) return;
    setCatalogueId(item.id);
    setCataloguePreview(item.imageUrl);
    setCategory(item.category);
    jewellery.selectRemote(item.imageUrl, `${item.id}.png`);
  };

  const uploadCustomJewellery = (file: File) => {
    setCatalogueId(null);
    setCataloguePreview(null);
    jewellery.select(file);
  };

  const clearJewellery = () => {
    setCatalogueId(null);
    setCataloguePreview(null);
    jewellery.clear();
  };

  const handleGenerate = async () => {
    if (!person.uploadId || !jewellery.uploadId || generating) return;
    setGenerating(true);
    setGenerateError(null);
    try {
      const tryOn = await generateTryOn(
        person.uploadId,
        jewellery.uploadId,
        category
      );
      setResult(tryOn);
    } catch (err) {
      setGenerateError(
        extractErrorMessage(err, "Generation failed. Please try again.")
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!result || downloading) return;
    setDownloading(true);
    setDownloadError(null);
    try {
      await downloadResult(result.result_id);
    } catch (err) {
      setDownloadError(
        extractErrorMessage(err, "Download failed. Please try again.")
      );
    } finally {
      setDownloading(false);
    }
  };

  const handleGenerateVideo = async () => {
    if (!result || generatingVideo) return;
    setGeneratingVideo(true);
    setVideoError(null);
    try {
      const generated = await generateVideo(result.result_id);
      setVideo(generated);
    } catch (err) {
      setVideoError(
        extractErrorMessage(err, "Video generation failed. Please try again.")
      );
    } finally {
      setGeneratingVideo(false);
    }
  };

  const handleDownloadVideo = async () => {
    if (!video || downloadingVideo) return;
    setDownloadingVideo(true);
    setVideoError(null);
    try {
      await downloadVideo(video.video_id);
    } catch (err) {
      setVideoError(
        extractErrorMessage(err, "Download failed. Please try again.")
      );
    } finally {
      setDownloadingVideo(false);
    }
  };

  const handleReset = () => {
    face.clear();
    hand.clear();
    clearJewellery();
    setResult(null);
    setGenerateError(null);
    setDownloadError(null);
    setVideo(null);
    setVideoError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 text-slate-900">
      <div className="mx-auto flex max-w-4xl flex-col gap-8 px-5 py-10 sm:py-16">
        <header className="flex flex-col items-center gap-3 text-center">
          <HealthBadge />
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            AI Virtual Jewellery Try-On
          </h1>
          <p className="max-w-md text-sm text-slate-500">
            Upload your photo and pick a jewellery item to preview the look
            instantly.
          </p>
        </header>

        <main className="rounded-3xl bg-white p-6 shadow-xl shadow-slate-200/60 sm:p-8">
          {result && person.previewUrl ? (
            <ResultView
              originalUrl={person.previewUrl}
              result={result}
              downloading={downloading}
              downloadError={downloadError}
              video={video}
              generatingVideo={generatingVideo}
              videoError={videoError}
              downloadingVideo={downloadingVideo}
              onDownload={handleDownload}
              onGenerateVideo={handleGenerateVideo}
              onDownloadVideo={handleDownloadVideo}
              onReset={handleReset}
            />
          ) : (
            <div className="flex flex-col gap-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <UploadCard
                  title="Face photo"
                  hint="For necklaces, earrings, glasses"
                  status={face.status}
                  previewUrl={face.previewUrl}
                  error={face.error}
                  disabled={generating}
                  active={bodyPart === "face"}
                  onSelect={face.select}
                  onClear={face.clear}
                />
                <UploadCard
                  title="Hand photo"
                  hint="For rings, bracelets, watches"
                  status={hand.status}
                  previewUrl={hand.previewUrl}
                  error={hand.error}
                  disabled={generating}
                  active={bodyPart === "hand"}
                  onSelect={hand.select}
                  onClear={hand.clear}
                />
              </div>

              <CategorySelector
                value={category}
                disabled={generating}
                onChange={(next) => {
                  setCategory(next);
                  setCatalogueId(null);
                }}
              />

              <CatalogueGrid
                selectedId={catalogueId}
                disabled={generating}
                onSelect={selectCatalogueItem}
              />

              <UploadCard
                title="Or upload your own jewellery"
                hint="Upload a jewellery image"
                status={jewellery.status}
                previewUrl={jewellery.previewUrl ?? cataloguePreview}
                error={jewellery.error}
                disabled={generating}
                onSelect={uploadCustomJewellery}
                onClear={clearJewellery}
              />

              {generateError && (
                <ErrorBanner message={generateError} onRetry={handleGenerate} />
              )}

              <button
                type="button"
                onClick={handleGenerate}
                disabled={!canGenerate}
                className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 py-3.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {generating ? (
                  <>
                    <Spinner /> Generating your try-on…
                  </>
                ) : (
                  "Generate try-on"
                )}
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
