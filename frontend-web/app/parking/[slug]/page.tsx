import Link from "next/link";
import { notFound } from "next/navigation";
import CameraCard from "../../components/CameraCard";
import { 
  NEIGHBORHOODS,
  getCamerasInNeighborhood,
  getNeighborhood,
  getNeighborhoodsWithCameras,
} from "../../lib/neighborhoods";

export function generateStaticParams() {
  return NEIGHBORHOODS.map((n) => ({ slug: n.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const n = getNeighborhood(slug);
  if (!n) return { title: "Neighborhood not found" };

  const path = `/parking/${n.slug}`;
  const title = `Parking in ${n.name}, ${n.borough} — Live Cameras`;
  const description = `Find street parking in ${n.name}, ${n.borough}. Live NYC DOT cameras covering the busiest intersections, plus local parking context and tips.`;

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

export default async function NeighborhoodPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const neighborhood = getNeighborhood(slug);
  if (!neighborhood) notFound();

  const cameras = getCamerasInNeighborhood(slug);
  const others = getNeighborhoodsWithCameras()
    .filter((n) => n.slug !== slug)
    .slice(0, 8);

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <nav className="mb-4 text-sm">
        <Link href="/parking" className="text-zinc-500 transition hover:text-orange-300">
          ← All neighborhoods
        </Link>
      </nav>

      <header className="mb-8 max-w-3xl">
        <div className="mb-2 font-mono text-xs uppercase tracking-widest text-zinc-500">
          {neighborhood.borough}
        </div>
        <h1 className="font-mono text-3xl font-black uppercase tracking-wider text-orange-300 sm:text-4xl">
          Parking in {neighborhood.name}
        </h1>
        <p className="mt-4 text-base leading-relaxed text-zinc-300">
          
        </p>
      </header>

      <section className="mb-12">
        <h2 className="mb-4 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
          Live cameras in {neighborhood.name}
          <span className="ml-2 text-zinc-600">({cameras.length})</span>
        </h2>

        {cameras.length === 0 ? (
          <p className="text-sm text-zinc-500">
            No NYC DOT cameras currently cover this area. Try a nearby
            neighborhood below.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {cameras.map((camera) => (
              <CameraCard key={camera.address} camera={camera} />
            ))}
          </div>
        )}
      </section>

      <section className="mb-12 max-w-3xl">
        <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
          Parking tips for {neighborhood.name}
        </h2>
        
        <p className="mt-4 text-xs text-zinc-500">
          Rules vary block by block. Always read posted signs before leaving
          your car. Alternate-side suspension days are listed on the{" "}
          <a
            href="https://www.nyc.gov/site/dot/motorists/parking.page"
            target="_blank"
            rel="noopener noreferrer"
            className="underline decoration-dotted underline-offset-2 hover:text-orange-300"
          >
            NYC DOT parking calendar
          </a>
          .
        </p>
      </section>

      {others.length > 0 ? (
        <section>
          <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-widest text-zinc-300">
            Other neighborhoods
          </h2>
          <ul className="flex flex-wrap gap-2 text-sm">
            {others.map((n) => (
              <li key={n.slug}>
                <Link
                  href={`/parking/${n.slug}`}
                  className="inline-block rounded-full border border-zinc-800 px-3 py-1.5 text-zinc-300 transition hover:border-orange-500/60 hover:text-orange-300"
                >
                  {n.name}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </main>
  );
}
