"use client";

import { useState } from "react";
import CameraCard from "../components/CameraCard";
import {
  findNearest,
  isWithinNYC,
  type Camera,
} from "../lib/cameras";

type NearCamera = Camera & { distanceMiles: number };

export default function NearestPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameras, setCameras] = useState<NearCamera[] | null>(null);

  const requestLocation = () => {
    if (!("geolocation" in navigator)) {
      setError("This browser does not support geolocation.");
      return;
    }
    setLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        if (!isWithinNYC(latitude, longitude)) {
          setError(
            "You appear to be outside NYC. This site only covers NYC DOT cameras.",
          );
          setLoading(false);
          return;
        }
        setCameras(findNearest(latitude, longitude, 6, 5));
        setLoading(false);
      },
      (err) => {
        setError(err.message || "Could not get your location.");
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 },
    );
  };

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6">
      <h1 className="font-mono text-2xl font-black uppercase tracking-widest text-orange-300 sm:text-3xl">
        Nearest cameras
      </h1>
      <p className="mt-2 max-w-xl text-sm text-zinc-400">
        Share your location and we&apos;ll show the closest DOT cameras. Nothing
        about your position is stored or sent to a server.
      </p>

      <div className="mt-6">
        <button
          type="button"
          onClick={requestLocation}
          disabled={loading}
          className="rounded-full border border-orange-500/60 bg-orange-500/10 px-5 py-2 font-medium text-orange-200 transition hover:bg-orange-500/20 disabled:opacity-50"
        >
          {loading ? "Locating…" : cameras ? "Refresh location" : "Use my location"}
        </button>
      </div>

      {error ? (
        <p className="mt-4 rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </p>
      ) : null}

      {cameras && cameras.length === 0 ? (
        <p className="mt-8 text-sm text-zinc-500">
          No cameras within 5 miles. Try browsing all cameras instead.
        </p>
      ) : null}

      {cameras && cameras.length > 0 ? (
        <section className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cameras.map((c) => (
            <CameraCard
              key={c.address}
              camera={c}
              subtitle={`${c.distanceMiles.toFixed(2)} mi away`}
            />
          ))}
        </section>
      ) : null}
    </main>
  );
}
