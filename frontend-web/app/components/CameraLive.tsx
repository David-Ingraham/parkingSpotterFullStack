"use client";

import { useState } from "react";
import { buildImageUrl } from "../lib/cameras";

type Props = {
  cameraId: string;
  alt: string;
  className?: string;
};

export default function CameraLive({ cameraId, alt, className }: Props) {
  const [stamp, setStamp] = useState<number>(() => Date.now());
  const [errored, setErrored] = useState(false);
  const [loading, setLoading] = useState(false);

  const refresh = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setErrored(false);
    setLoading(true);
    setStamp(Date.now());
  };

  const src = buildImageUrl(cameraId, stamp);

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
          key={src}
          src={src}
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
    </div>
  );
}
