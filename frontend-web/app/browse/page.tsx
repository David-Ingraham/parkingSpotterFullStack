"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { getAllCameras } from "../lib/cameras";

const PAGE_SIZE = 24;

export default function BrowsePage() {
  const all = useMemo(() => getAllCameras(), []);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return all;
    return all.filter(
      (c) =>
        c.displayName.toLowerCase().includes(q) ||
        c.address.toLowerCase().includes(q),
    );
  }, [all, query]);

  const start = page * PAGE_SIZE;
  const end = start + PAGE_SIZE;
  const paged = filtered.slice(start, end);
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
      <div className="mb-6">
        <h1 className="font-mono text-2xl font-black uppercase tracking-widest text-orange-300">
          Browse cameras
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          {filtered.length} of {all.length} NYC DOT cameras
        </p>
      </div>

      <input
        type="search"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setPage(0);
        }}
        placeholder="Filter by street or intersection"
        autoComplete="off"
        spellCheck={false}
        className="mb-6 w-full rounded-lg border border-zinc-800 bg-zinc-950 px-4 py-3 text-base text-zinc-100 placeholder:text-zinc-600 focus:border-orange-500/60 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
      />

      <ul className="divide-y divide-zinc-900 rounded-lg border border-zinc-900">
        {paged.length === 0 ? (
          <li className="px-4 py-6 text-sm text-zinc-500">
            No cameras match that search.
          </li>
        ) : (
          paged.map((camera) => (
            <li key={camera.address}>
              <Link
                href={`/camera/${encodeURIComponent(camera.address)}`}
                className="flex items-center justify-between gap-3 px-4 py-3 transition hover:bg-zinc-900"
              >
                <div className="min-w-0">
                  <div className="truncate text-zinc-100">
                    {camera.displayName}
                  </div>
                  <div className="mt-0.5 font-mono text-[10px] text-zinc-600">
                    {camera.latitude.toFixed(4)}, {camera.longitude.toFixed(4)}
                  </div>
                </div>
                <span className="shrink-0 text-xs text-zinc-500">View →</span>
              </Link>
            </li>
          ))
        )}
      </ul>

      {totalPages > 1 ? (
        <div className="mt-6 flex items-center justify-between text-sm">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="rounded-md border border-zinc-800 px-3 py-1.5 text-zinc-300 transition hover:border-zinc-600 disabled:opacity-40"
          >
            ← Prev
          </button>
          <span className="text-zinc-500">
            Page {page + 1} of {totalPages}
          </span>
          <button
            type="button"
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="rounded-md border border-zinc-800 px-3 py-1.5 text-zinc-300 transition hover:border-zinc-600 disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      ) : null}
    </main>
  );
}
