"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { searchCameras, type Camera } from "../lib/cameras";

type Props = {
  initialQuery?: string;
  placeholder?: string;
  showResults?: boolean;
  onSelect?: (camera: Camera) => void;
};

export default function SearchBar({
  initialQuery = "",
  placeholder = "Search by street or intersection",
  showResults = true,
  onSelect,
}: Props) {
  const [query, setQuery] = useState(initialQuery);
  const results = useMemo(() => searchCameras(query), [query]);

  return (
    <div className="w-full">
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        autoComplete="off"
        spellCheck={false}
        className="w-full rounded-lg border border-zinc-800 bg-zinc-950 px-4 py-3 text-base text-zinc-100 placeholder:text-zinc-600 focus:border-orange-500/60 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
      />

      {showResults && query.trim() ? (
        <ul className="mt-2 max-h-96 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950 shadow-lg">
          {results.length === 0 ? (
            <li className="px-4 py-3 text-sm text-zinc-500">No matches</li>
          ) : (
            results.map((camera) => {
              const inner = (
                <div className="flex items-center justify-between px-4 py-3 transition hover:bg-zinc-900">
                  <span className="truncate text-zinc-100">
                    {camera.displayName}
                  </span>
                  <span className="ml-3 shrink-0 text-xs text-zinc-500">
                    View
                  </span>
                </div>
              );
              if (onSelect) {
                return (
                  <li key={camera.address}>
                    <button
                      type="button"
                      onClick={() => onSelect(camera)}
                      className="block w-full text-left"
                    >
                      {inner}
                    </button>
                  </li>
                );
              }
              return (
                <li key={camera.address}>
                  <Link
                    href={`/camera/${encodeURIComponent(camera.address)}`}
                    className="block"
                  >
                    {inner}
                  </Link>
                </li>
              );
            })
          )}
        </ul>
      ) : null}
    </div>
  );
}
