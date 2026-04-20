import Link from "next/link";
import type { Camera } from "../lib/cameras";
import CameraLive from "./CameraLive";

type Props = {
  camera: Camera;
  subtitle?: string;
};

export default function CameraCard({ camera, subtitle }: Props) {
  return (
    <Link
      href={`/camera/${encodeURIComponent(camera.address)}`}
      className="group block overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950 transition hover:border-orange-500/60 hover:shadow-[0_0_32px_-8px_rgba(249,115,22,0.5)]"
    >
      <div className="aspect-video">
        <CameraLive
          cameraId={camera.camera_id}
          alt={camera.displayName}
          className="h-full"
        />
      </div>
      <div className="flex items-start justify-between gap-3 px-4 py-3">
        <div className="min-w-0">
          <div className="truncate font-semibold text-zinc-100 group-hover:text-orange-300">
            {camera.displayName}
          </div>
          {subtitle ? (
            <div className="mt-0.5 text-xs text-zinc-500">{subtitle}</div>
          ) : null}
        </div>
        <span className="shrink-0 text-xs text-zinc-600 group-hover:text-orange-400">
          View →
        </span>
      </div>
    </Link>
  );
}
