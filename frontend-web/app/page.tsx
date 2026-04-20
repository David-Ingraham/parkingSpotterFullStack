import Link from "next/link";
import CameraCard from "./components/CameraCard";
import SearchBar from "./components/SearchBar";
import { getFeaturedCameras } from "./lib/cameras";

export default function Home() {
  const featured = getFeaturedCameras();

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <section className="mb-10 sm:mb-14">
        <div className="max-w-xl">
          <SearchBar placeholder="Search a street, e.g. Houston St Bowery" />
        </div>

        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <Link
            href="/nearest"
            className="rounded-full border border-orange-500/40 px-4 py-1.5 text-orange-300 transition hover:border-orange-400 hover:bg-orange-500/10"
          >
            Nearest to me
          </Link>
          <Link
            href="/browse"
            className="rounded-full border border-zinc-700 px-4 py-1.5 text-zinc-300 transition hover:border-zinc-500"
          >
            Browse all cameras
          </Link>
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-baseline justify-between">
          <h2 className="font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
            Featured feeds
          </h2>
          <span className="text-xs text-zinc-600">
            High-demand parking blocks
          </span>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {featured.map((camera) => (
            <CameraCard key={camera.address} camera={camera} />
          ))}
        </div>
      </section>

      <footer className="mt-16 border-t border-zinc-900 pt-6 text-xs text-zinc-600">
        Images served from NYC DOT traffic cameras. Refresh a camera page for a
        newer frame.
      </footer>
    </main>
  );
}
