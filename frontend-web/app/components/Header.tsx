import Link from "next/link";

export default function Header() {
  return (
    <header className="sticky top-0 z-30 border-b border-zinc-900 bg-black/70 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <Link
          href="/"
          className="font-mono text-lg font-black uppercase tracking-widest text-orange-300"
        >
          Parking Spotter
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <Link
            href="/parking"
            className="text-zinc-400 transition hover:text-orange-300"
          >
            Neighborhoods
          </Link>
          <Link
            href="/browse"
            className="text-zinc-400 transition hover:text-orange-300"
          >
            Browse
          </Link>
          <Link
            href="/nearest"
            className="text-zinc-400 transition hover:text-orange-300"
          >
            Nearest
          </Link>
        </div>
      </nav>
    </header>
  );
}
