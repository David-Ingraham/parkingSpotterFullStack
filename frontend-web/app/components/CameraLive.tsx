"use client";

import { useState } from "react";
import { buildImageUrl } from "../lib/cameras";
import { InferenceError, InferResponse, runInference } from "../lib/inference";

type Props = {
  cameraId: string;
  alt: string;
  className?: string;
  address?: string;
};

type InferState =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "done"; result: InferResponse }
  | { kind: "error"; message: string };

function resultBadgeClasses(status: boolean | null): string {
  if (status === true) {
    return "border-emerald-500/50 bg-emerald-950/80 text-emerald-300";
  }
  if (status === false) {
    return "border-amber-500/50 bg-amber-950/80 text-amber-300";
  }
  return "border-zinc-600/50 bg-zinc-950/80 text-zinc-400";
}

export default function CameraLive({ cameraId, alt, className, address }: Props) {
  const [stamp, setStamp] = useState<number>(() => Date.now());
  const [errored, setErrored] = useState(false);
  const [loading, setLoading] = useState(false);
  const [inferState, setInferState] = useState<InferState>({ kind: "idle" });
  const [showAnnotated, setShowAnnotated] = useState(false);

  const refresh = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setErrored(false);
    setLoading(true);
    setInferState({ kind: "idle" });
    setShowAnnotated(false);
    setStamp(Date.now());
  };

  const analyze = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!address || inferState.kind === "running") return;

    setInferState({ kind: "running" });
    setShowAnnotated(false);
    try {
      const result = await runInference(address, stamp);
      setInferState({ kind: "done", result });
      if (result.annotated_image_base64) {
        setShowAnnotated(true);
      }
    } catch (err) {
      const msg = err instanceof InferenceError ? err.message : "Something went wrong.";
      setInferState({ kind: "error", message: msg });
    }
  };

  const src = buildImageUrl(cameraId, stamp);
  const annotatedSrc =
    inferState.kind === "done" && inferState.result.annotated_image_base64
      ? `data:image/jpeg;base64,${inferState.result.annotated_image_base64}`
      : null;
  const displaySrc = showAnnotated && annotatedSrc ? annotatedSrc : src;

  return (
    <div
      className={`relative w-full overflow-hidden bg-zinc-900 ${className ?? ""}`}
    >
      {errored ? (
        <div className="flex h-full w-full items-center justify-center p-6 text-center text-sm text-zinc-400">
          Feed unavailable. DOT cameras occasionally go offline.
        </div>
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          key={showAnnotated && annotatedSrc ? annotatedSrc : src}
          src={displaySrc}
          alt={alt}
          onError={() => {
            setErrored(true);
            setLoading(false);
          }}
          onLoad={() => setLoading(false)}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      )}

      {address ? (
        <button
          type="button"
          onClick={analyze}
          disabled={errored || inferState.kind === "running"}
          aria-label="Analyze current frame for parking"
          className="absolute bottom-2 right-2 flex items-center gap-1.5 rounded-full bg-black/70 px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-orange-300 shadow-md backdrop-blur transition hover:bg-black/90 hover:text-orange-200 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <svg
            viewBox="0 0 24 24"
            className={`h-3 w-3 ${inferState.kind === "running" ? "animate-pulse" : ""}`}
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M12 2a4 4 0 0 1 4 4v1a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z" />
            <path d="M8 11h8" />
            <path d="M12 11v9" />
            <path d="M8 20h8" />
          </svg>
          {inferState.kind === "running" ? "Analyzing..." : "Analyze"}
        </button>
      ) : null}

      <button
        type="button"
        onClick={refresh}
        aria-label="Refresh camera image"
        className="absolute right-2 top-2 flex items-center gap-1.5 rounded-full bg-black/70 px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-orange-300 shadow-md backdrop-blur transition hover:bg-black/90 hover:text-orange-200 active:scale-95"
      >
        <svg
          viewBox="0 0 24 24"
          className={`h-3 w-3 ${loading ? "animate-spin" : ""}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M21 12a9 9 0 1 1-3.1-6.8" />
          <path d="M21 3v6h-6" />
        </svg>
        Refresh
      </button>

      {inferState.kind === "done" ? (
        <div className="absolute bottom-2 left-2 flex max-w-[calc(100%-5rem)] flex-col gap-1">
          <div
            className={`rounded-full border px-2.5 py-1 text-[11px] font-medium shadow-md backdrop-blur ${resultBadgeClasses(inferState.result.open_parking_status)}`}
          >
            {inferState.result.label}
          </div>
          {annotatedSrc ? (
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowAnnotated((v) => !v);
              }}
              className="w-fit rounded-full bg-black/70 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-zinc-300 shadow-md backdrop-blur transition hover:bg-black/90"
            >
              {showAnnotated ? "Show live" : "Show boxes"}
            </button>
          ) : null}
        </div>
      ) : null}

      {inferState.kind === "error" ? (
        <div className="absolute bottom-2 left-2 max-w-[calc(100%-5rem)] rounded-full border border-red-500/50 bg-red-950/80 px-2.5 py-1 text-[11px] font-medium text-red-300 shadow-md backdrop-blur">
          {inferState.message}
        </div>
      ) : null}
    </div>
  );
}
