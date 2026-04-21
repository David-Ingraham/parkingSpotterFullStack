export const WATCH_DURATIONS = [30, 60, 90] as const;
export type WatchDuration = (typeof WATCH_DURATIONS)[number];

type WatchRequest = {
  address: string;
  email: string;
  minutes: WatchDuration;
};

export type WatchResponse = {
  status: "ok";
  address: string;
  expires_at_utc: string;
  watcher_count: number;
};

export class WatchlistError extends Error {
  constructor(message: string, public readonly statusCode?: number) {
    super(message);
  }
}

function getApiConfig(): { url: string; key: string } {
  const url = process.env.NEXT_PUBLIC_WATCHER_API_URL;
  const key = process.env.NEXT_PUBLIC_WATCHER_API_KEY;
  if (!url || !key) {
    throw new WatchlistError(
      "Watchlist API is not configured. Set NEXT_PUBLIC_WATCHER_API_URL and NEXT_PUBLIC_WATCHER_API_KEY.",
    );
  }
  return { url: url.replace(/\/$/, ""), key };
}

export async function submitWatch(req: WatchRequest): Promise<WatchResponse> {
  const { url, key } = getApiConfig();

  let res: Response;
  try {
    res = await fetch(`${url}/watch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key,
      },
      body: JSON.stringify(req),
    });
  } catch (err) {
    throw new WatchlistError("Could not reach the watchlist server. Try again in a moment.");
  }

  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    /* body may be empty on 401/5xx */
  }

  if (!res.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body && typeof (body as { detail: unknown }).detail === "string"
        ? (body as { detail: string }).detail
        : `Server returned ${res.status}`;
    throw new WatchlistError(detail, res.status);
  }

  return body as WatchResponse;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(value: string): boolean {
  return EMAIL_REGEX.test(value.trim());
}
