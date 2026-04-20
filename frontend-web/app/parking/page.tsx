import Link from "next/link";
import type { Metadata } from "next";
import { getNeighborhoodsWithCameras } from "../lib/neighborhoods";

export const metadata: Metadata = {
  title: "Parking by Neighborhood — NYC",
  description:
    "Find street parking in NYC by neighborhood. Live DOT cameras and local parking context for SoHo, East Village, Williamsburg, Park Slope, Astoria, and more.",
  alternates: { canonical: "/parking" },
  openGraph: {
    type: "website",
    url: "/parking",
    title: "Parking by Neighborhood — NYC",
    description:
      "Find street parking in NYC by neighborhood. Live DOT cameras and local parking context.",
  },
};

export default function ParkingIndex() {
  const neighborhoods = getNeighborhoodsWithCameras();
  const byBorough = neighborhoods.reduce<Record<string, typeof neighborhoods>>(
    (acc, n) => {
      (acc[n.borough] ||= []).push(n);
      return acc;
    },
    {},
  );
  const boroughOrder = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"];

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6 sm:py-14">
      <header className="mb-10 max-w-2xl">
        <h1 className="font-mono text-3xl font-black uppercase tracking-wider text-orange-300 sm:text-4xl">
          Parking by neighborhood
        </h1>
        <p className="mt-4 text-base leading-relaxed text-zinc-300">
          Each neighborhood page aggregates the live NYC DOT cameras that cover
          its busiest intersections, with local context about where parking
          tends to be easier and when demand peaks. Pick a neighborhood below.
        </p>
      </header>

      {boroughOrder
        .filter((b) => byBorough[b]?.length)
        .map((borough) => (
          <section key={borough} className="mb-10">
            <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
              {borough}
            </h2>
            <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {byBorough[borough].map((n) => (
                <li key={n.slug}>
                  <Link
                    href={`/parking/${n.slug}`}
                    className="flex items-baseline justify-between rounded-lg border border-zinc-800 bg-zinc-950 px-4 py-3 transition hover:border-orange-500/60 hover:bg-zinc-900"
                  >
                    <span className="text-zinc-100">{n.name}</span>
                    <span className="text-xs text-zinc-500">
                      {n.cameraCount} cam{n.cameraCount === 1 ? "" : "s"}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ))}
    </main>
  );
}
