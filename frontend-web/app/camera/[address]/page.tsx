import Link from "next/link";
import { notFound } from "next/navigation";
import CameraLive from "../../components/CameraLive";
import WatchlistButton from "../../components/WatchlistButton";
import {
  getAllCameras,
  getCamera,
  findNearest,
  FEATURED_ADDRESSES,
} from "../../lib/cameras";
import { getNeighborhoodForCamera } from "../../lib/neighborhoods";

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

  const neighborhood = getNeighborhoodForCamera(camera);
  const locationLabel = neighborhood
    ? `${neighborhood.name}, ${neighborhood.borough}`
    : "NYC";

  const path = `/camera/${encodeURIComponent(camera.address)}`;
  const title = `Parking at ${camera.displayName} — Live ${locationLabel} Camera`;
  const description = `Live NYC DOT traffic camera at ${camera.displayName} in ${locationLabel}. Check current street conditions before driving to find parking near this intersection.`;

  return {
    title,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "website",
      url: path,
      title,
      description,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
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

  const neighborhood = getNeighborhoodForCamera(camera);
  const nearby = findNearest(camera.latitude, camera.longitude, 6, 1.5).filter(
    (c) => c.address !== camera.address,
  );

  const isFeatured = FEATURED_ADDRESSES.includes(camera.address);

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6">
      <nav className="mb-4 flex items-center gap-3 text-sm">
        <Link href="/" className="text-zinc-500 transition hover:text-orange-300">
          ← Home
        </Link>
        {neighborhood ? (
          <>
            <span className="text-zinc-700">/</span>
            <Link
              href={`/parking/${neighborhood.slug}`}
              className="text-zinc-500 transition hover:text-orange-300"
            >
              {neighborhood.name}
            </Link>
          </>
        ) : null}
      </nav>

      <div className="mb-6">
        <h1 className="font-mono text-2xl font-black uppercase tracking-wider text-orange-300 sm:text-3xl">
          {camera.displayName}
        </h1>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-zinc-500">
          {neighborhood ? (
            <span>
              {neighborhood.name},{" "}
              <span className="text-zinc-600">{neighborhood.borough}</span>
            </span>
          ) : null}
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
        <div className="relative aspect-video">
          <CameraLive
            cameraId={camera.camera_id}
            alt={camera.displayName}
            className="h-full"
          />
          <WatchlistButton
            address={camera.address}
            displayName={camera.displayName}
            variant="compact"
          />
        </div>
      </div>

      <p className="mt-3 text-xs text-zinc-600">
        Tap Refresh on the image for a newer frame. Images pulled directly from
        NYC DOT.
      </p>

      <div className="mt-4">
        <WatchlistButton
          address={camera.address}
          displayName={camera.displayName}
          variant="full"
        />
      </div>

      <section className="mt-10 max-w-3xl">
        <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
          About this location
        </h2>
        <p className="text-sm leading-relaxed text-zinc-300">
          This live camera covers {camera.displayName}
          {neighborhood ? ` in ${neighborhood.name}, ${neighborhood.borough}` : ""}.
          Use the feed to see whether the block is already lined solid or
          whether traffic has cleared enough to attempt a pass. Camera images
          are published by NYC DOT and refresh when you tap Refresh.
        </p>

        {neighborhood ? (
          <div className="mt-4">
            <Link
              href={`/parking/${neighborhood.slug}`}
              className="inline-flex items-center gap-2 rounded-full border border-orange-500/40 px-4 py-1.5 text-sm text-orange-300 transition hover:border-orange-400 hover:bg-orange-500/10"
            >
              More parking in {neighborhood.name} →
            </Link>
          </div>
        ) : null}
      </section>

      <section className="mt-10 max-w-3xl">
        <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
          Before you park
        </h2>
        <ul className="space-y-2 text-sm leading-relaxed text-zinc-300">
          <li className="flex gap-3">
            <span className="mt-1 shrink-0 text-orange-400">•</span>
            <span>
              Read the posted signs. Parking rules change block to block and
              this camera cannot tell you what the regulation is on a specific
              spot.
            </span>
          </li>
          <li className="flex gap-3">
            <span className="mt-1 shrink-0 text-orange-400">•</span>
            <span>
              Alternate-side street cleaning is suspended on holidays and
              during snow emergencies — see the{" "}
              <a
                href="https://www.nyc.gov/site/dot/motorists/parking.page"
                target="_blank"
                rel="noopener noreferrer"
                className="underline decoration-dotted underline-offset-2 hover:text-orange-300"
              >
                NYC DOT parking calendar
              </a>
              .
            </span>
          </li>
          <li className="flex gap-3">
            <span className="mt-1 shrink-0 text-orange-400">•</span>
            <span>
              Bus lanes, bike lanes, and fire hydrants are camera-enforced. Do
              not stop in them, even briefly.
            </span>
          </li>
        </ul>
      </section>

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
