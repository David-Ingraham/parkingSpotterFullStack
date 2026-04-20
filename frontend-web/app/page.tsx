import Link from "next/link";
import CameraCard from "./components/CameraCard";
import SearchBar from "./components/SearchBar";
import { getFeaturedCameras } from "./lib/cameras";
import { getNeighborhoodsWithCameras } from "./lib/neighborhoods";

export default function Home() {
  const featured = getFeaturedCameras();
  const neighborhoods = getNeighborhoodsWithCameras().slice(0, 12);

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <section className="mb-12 max-w-3xl sm:mb-16">
        <h1 className="font-mono text-3xl font-black uppercase tracking-wider text-orange-300 sm:text-5xl">
          Find street parking in NYC.
        </h1>
        <p className="mt-5 text-base leading-relaxed text-zinc-300 sm:text-lg">
          Parking Spotter shows you live NYC DOT traffic cameras for the streets
          and intersections where parking is hardest — so you can see whether a
          block is already full before you drive there. No signup, no app
          install, free to use.
        </p>

        <div className="mt-8 max-w-xl">
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
            href="/parking"
            className="rounded-full border border-zinc-700 px-4 py-1.5 text-zinc-300 transition hover:border-zinc-500"
          >
            By neighborhood
          </Link>
          <Link
            href="/browse"
            className="rounded-full border border-zinc-700 px-4 py-1.5 text-zinc-300 transition hover:border-zinc-500"
          >
            Browse all cameras
          </Link>
        </div>
      </section>

      <section className="mb-14">
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

      {neighborhoods.length > 0 ? (
        <section className="mb-14">
          <div className="mb-4 flex items-baseline justify-between">
            <h2 className="font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
              Parking by neighborhood
            </h2>
            <Link
              href="/parking"
              className="text-xs text-zinc-500 transition hover:text-orange-300"
            >
              All neighborhoods →
            </Link>
          </div>
          <ul className="flex flex-wrap gap-2 text-sm">
            {neighborhoods.map((n) => (
              <li key={n.slug}>
                <Link
                  href={`/parking/${n.slug}`}
                  className="inline-flex items-baseline gap-2 rounded-full border border-zinc-800 bg-zinc-950 px-4 py-1.5 text-zinc-200 transition hover:border-orange-500/60 hover:text-orange-300"
                >
                  <span>{n.name}</span>
                  <span className="text-xs text-zinc-600">
                    {n.cameraCount}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="mb-10 max-w-3xl">
        <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
          How it works
        </h2>
        <p className="text-sm leading-relaxed text-zinc-400">
          NYC DOT publishes live camera feeds at hundreds of intersections
          citywide. Parking Spotter picks out the cameras that cover streets
          with heavy parking demand — near bars, restaurants, markets, transit
          hubs, and dense residential blocks — and groups them by neighborhood.
          Pick a feed, glance at the block, decide whether it is worth the
          drive. Images come straight from NYC DOT and refresh on demand.
        </p>
      </section>

      <footer className="mt-16 border-t border-zinc-900 pt-6 text-xs text-zinc-600">
        Images served from NYC DOT traffic cameras. Refresh a camera page for a
        newer frame. Parking rules vary block to block — always read posted
        signs before leaving your car.
      </footer>
    </main>
  );
}
