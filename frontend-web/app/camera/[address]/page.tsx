import Link from "next/link";
import { notFound } from "next/navigation";
import CameraLive from "../../components/CameraLive";
import {
  getAllCameras,
  getCamera,
  findNearest,
  FEATURED_ADDRESSES,
} from "../../lib/cameras";

export function generateStaticParams() {
  return getAllCameras().map((c) => ({ address: c.address }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ address: string }>;
}) {
  const { address } = await params;
  const decoded = decodeURIComponent(address);
  const camera = getCamera(decoded);
  if (!camera) return { title: "Camera not found" };
  return {
    title: `${camera.displayName} — Parking Spotter`,
    description: `Live NYC DOT camera at ${camera.displayName}.`,
  };
}

export default async function CameraDetail({
  params,
}: {
  params: Promise<{ address: string }>;
}) {
  const { address } = await params;
  const decoded = decodeURIComponent(address);
  const camera = getCamera(decoded);
  if (!camera) notFound();

  const nearby = findNearest(camera.latitude, camera.longitude, 6, 1.5).filter(
    (c) => c.address !== camera.address,
  );

  const isFeatured = FEATURED_ADDRESSES.includes(camera.address);

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6">
      <nav className="mb-4 text-sm">
        <Link href="/" className="text-zinc-500 transition hover:text-orange-300">
          ← Home
        </Link>
      </nav>

      <div className="mb-6">
        <h1 className="font-mono text-2xl font-black uppercase tracking-wider text-orange-300 sm:text-3xl">
          {camera.displayName}
        </h1>
        <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-zinc-500">
          <span className="font-mono">
            {camera.latitude.toFixed(5)}, {camera.longitude.toFixed(5)}
          </span>
          {isFeatured ? (
            <span className="rounded-full border border-orange-500/40 px-2 py-0.5 text-orange-300">
              Featured
            </span>
          ) : null}
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-zinc-800 bg-black">
        <div className="aspect-video">
          <CameraLive
            cameraId={camera.camera_id}
            alt={camera.displayName}
            className="h-full"
          />
        </div>
      </div>

      <p className="mt-3 text-xs text-zinc-600">
        Tap Refresh on the image for a newer frame. Images pulled directly from
        NYC DOT.
      </p>

      {nearby.length > 0 ? (
        <section className="mt-10">
          <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
            Nearby cameras
          </h2>
          <ul className="divide-y divide-zinc-900 rounded-lg border border-zinc-900">
            {nearby.map((c) => (
              <li key={c.address}>
                <Link
                  href={`/camera/${encodeURIComponent(c.address)}`}
                  className="flex items-center justify-between gap-3 px-4 py-3 transition hover:bg-zinc-900"
                >
                  <div className="min-w-0">
                    <div className="truncate text-zinc-100">
                      {c.displayName}
                    </div>
                    <div className="mt-0.5 text-[11px] text-zinc-600">
                      {c.distanceMiles.toFixed(2)} mi away
                    </div>
                  </div>
                  <span className="shrink-0 text-xs text-zinc-500">View →</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </main>
  );
}
