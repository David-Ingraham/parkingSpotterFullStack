export type InferResponse = {
  address: string;
  open_parking_status: boolean | null;
  label: string;
  annotated_image_base64: string | null;
};

export class InferenceError extends Error {
  constructor(message: string, public readonly statusCode?: number) {
    super(message);
  }
}

function getApiConfig(): { url: string; key: string } {
  const url = process.env.NEXT_PUBLIC_WATCHER_API_URL;
  const key = process.env.NEXT_PUBLIC_WATCHER_API_KEY;
  if (!url || !key) {
    throw new InferenceError(
      "Inference API is not configured. Set NEXT_PUBLIC_WATCHER_API_URL and NEXT_PUBLIC_WATCHER_API_KEY.",
    );
  }
  return { url: url.replace(/\/$/, ""), key };
}

export async function runInference(
  address: string,
  stamp: number,
): Promise<InferResponse> {
  const { url, key } = getApiConfig();

  let res: Response;
  try {
    res = await fetch(`${url}/infer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key,
      },
      body: JSON.stringify({ address, t: stamp }),
    });
  } catch {
    throw new InferenceError("Could not reach the inference server. Try again in a moment.");
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
    throw new InferenceError(detail, res.status);
  }

  return body as InferResponse;
}
