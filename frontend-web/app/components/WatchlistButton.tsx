"use client";

import { useEffect, useRef, useState } from "react";
import {
  WATCH_DURATIONS,
  WatchDuration,
  WatchlistError,
  isValidEmail,
  submitWatch,
} from "../lib/watchlist";

type Props = {
  address: string;
  displayName: string;
  variant?: "compact" | "full";
};

type Status =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; expiresAt: string; minutes: WatchDuration }
  | { kind: "error"; message: string };

export default function WatchlistButton({ address, displayName, variant = "compact" }: Props) {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [minutes, setMinutes] = useState<WatchDuration>(30);
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const toggle = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setOpen((v) => !v);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const trimmed = email.trim();
    if (!isValidEmail(trimmed)) {
      setStatus({ kind: "error", message: "Enter a valid email address." });
      return;
    }
    setStatus({ kind: "submitting" });
    try {
      const res = await submitWatch({ address, email: trimmed, minutes });
      setStatus({ kind: "success", expiresAt: res.expires_at_utc, minutes });
    } catch (err) {
      const msg = err instanceof WatchlistError ? err.message : "Something went wrong.";
      setStatus({ kind: "error", message: msg });
    }
  };

  const triggerClasses =
    variant === "compact"
      ? "absolute left-2 top-2 z-20 flex items-center gap-1.5 rounded-full bg-black/70 px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-orange-300 shadow-md backdrop-blur transition hover:bg-black/90 hover:text-orange-200 active:scale-95"
      : "inline-flex items-center gap-2 rounded-full border border-orange-500/40 px-4 py-1.5 text-sm text-orange-300 transition hover:border-orange-400 hover:bg-orange-500/10";

  return (
    <div ref={rootRef} className={variant === "compact" ? "contents" : "relative inline-block"}>
      <button
        type="button"
        onClick={toggle}
        aria-expanded={open}
        aria-haspopup="dialog"
        className={triggerClasses}
      >
        <svg
          viewBox="0 0 24 24"
          className="h-3 w-3"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M12 6v6l4 2" />
          <circle cx="12" cy="12" r="9" />
        </svg>
        {variant === "compact" ? "Watch" : "Add to watch list"}
      </button>

      {open ? (
        <div
          role="dialog"
          aria-label={`Watch list for ${displayName}`}
          onClick={(e) => e.stopPropagation()}
          className={
            variant === "compact"
              ? "absolute left-2 top-10 z-30 w-[260px] max-h-[calc(100vh-5rem)] overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950 p-3 shadow-xl"
              : "absolute left-0 top-12 z-30 w-[300px] max-h-[calc(100vh-5rem)] overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950 p-3 shadow-xl"
          }
        >
          {status.kind === "success" ? (
            <SuccessPanel
              minutes={status.minutes}
              expiresAt={status.expiresAt}
              onClose={() => {
                setOpen(false);
                setStatus({ kind: "idle" });
              }}
            />
          ) : (
            <form onSubmit={submit} className="space-y-3">
              <div>
                <div className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-zinc-400">
                  Email
                </div>
                <input
                  type="email"
                  required
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full rounded border border-zinc-800 bg-black px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-orange-500/60"
                />
              </div>

              <div>
                <div className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-zinc-400">
                  Watch for
                </div>
                <div className="grid grid-cols-3 gap-1.5">
                  {WATCH_DURATIONS.map((d) => {
                    const active = d === minutes;
                    return (
                      <button
                        key={d}
                        type="button"
                        onClick={() => setMinutes(d)}
                        className={
                          active
                            ? "rounded border border-orange-500 bg-orange-500/10 px-2 py-1 text-xs font-semibold text-orange-200"
                            : "rounded border border-zinc-800 bg-black px-2 py-1 text-xs text-zinc-300 hover:border-zinc-600"
                        }
                      >
                        {d} min
                      </button>
                    );
                  })}
                </div>
              </div>

              {status.kind === "error" ? (
                <div className="text-xs text-red-400">{status.message}</div>
              ) : null}

              <button
                type="submit"
                disabled={status.kind === "submitting"}
                className="w-full rounded bg-orange-500 px-3 py-1.5 text-sm font-semibold text-black transition hover:bg-orange-400 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {status.kind === "submitting" ? "Adding..." : "Notify me by email"}
              </button>

              <p className="text-[10px] leading-snug text-zinc-500">
              You'll get an email when a spot opens up
              </p>
            </form>
          )}
        </div>
      ) : null}
    </div>
  );
}

function SuccessPanel({
  minutes,
  expiresAt,
  onClose,
}: {
  minutes: WatchDuration;
  expiresAt: string;
  onClose: () => void;
}) {
  const expiresLocal = new Date(expiresAt).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold text-orange-300">Watching for {minutes} min</div>
      <p className="text-xs text-zinc-400">
        We will email you if the model sees an open spot before {expiresLocal}.
      </p>
      <button
        type="button"
        onClick={onClose}
        className="w-full rounded border border-zinc-800 px-3 py-1.5 text-xs text-zinc-300 hover:border-zinc-600"
      >
        Close
      </button>
    </div>
  );
}
