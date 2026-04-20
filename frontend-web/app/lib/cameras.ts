import rawCameras from "../data/cameras.json";

export type CameraRecord = {
  camera_id: string;
  latitude: number;
  longitude: number;
  formatted_address?: string;
};

export type Camera = CameraRecord & {
  address: string;
  displayName: string;
};

const CAMERA_DATA = rawCameras as Record<string, CameraRecord>;

const DOT_IMAGE_BASE = "https://webcams.nyctmc.org/api/cameras";

export const FEATURED_ADDRESSES: readonly string[] = [
  "Grand_St_Bowery",
  "Wythe_Ave_North_12_St",
  "Canal_St_Broadway",
  "West_Houston_Hudson_St",
  "1_Ave_86_St",
  "Flatbush_Ave_Nostrand_Ave",
] as const;

export const NYC_BOUNDS = {
  latMin: 40.4774,
  latMax: 40.9176,
  lngMin: -74.2591,
  lngMax: -73.7004,
} as const;

export function formatAddress(address: string): string {
  return address
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\bSt\b/g, "St")
    .replace(/\bAve\b/g, "Ave");
}

export function toCamera(address: string, record: CameraRecord): Camera {
  return {
    ...record,
    address,
    displayName: record.formatted_address?.trim() || formatAddress(address),
  };
}

export function getAllCameras(): Camera[] {
  return Object.entries(CAMERA_DATA)
    .filter(([, v]) => typeof v.latitude === "number" && typeof v.longitude === "number")
    .map(([address, record]) => toCamera(address, record));
}

export function getCamera(address: string): Camera | null {
  const record = CAMERA_DATA[address];
  if (!record) return null;
  return toCamera(address, record);
}

export function getFeaturedCameras(): Camera[] {
  return FEATURED_ADDRESSES.map((a) => getCamera(a)).filter(
    (c): c is Camera => c !== null,
  );
}

export function buildImageUrl(cameraId: string, cacheBuster: number): string {
  return `${DOT_IMAGE_BASE}/${cameraId}/image?t=${cacheBuster}`;
}

export function isWithinNYC(lat: number, lng: number): boolean {
  return (
    lat >= NYC_BOUNDS.latMin &&
    lat <= NYC_BOUNDS.latMax &&
    lng >= NYC_BOUNDS.lngMin &&
    lng <= NYC_BOUNDS.lngMax
  );
}

export function haversineMiles(
  aLat: number,
  aLng: number,
  bLat: number,
  bLng: number,
): number {
  const R = 3958.7613;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(bLat - aLat);
  const dLng = toRad(bLng - aLng);
  const lat1 = toRad(aLat);
  const lat2 = toRad(bLat);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

export function findNearest(
  lat: number,
  lng: number,
  limit = 5,
  maxMiles = 7,
): Array<Camera & { distanceMiles: number }> {
  return getAllCameras()
    .map((camera) => ({
      ...camera,
      distanceMiles: haversineMiles(lat, lng, camera.latitude, camera.longitude),
    }))
    .filter((c) => c.distanceMiles <= maxMiles)
    .sort((a, b) => a.distanceMiles - b.distanceMiles)
    .slice(0, limit);
}

export function searchCameras(query: string): Camera[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const all = getAllCameras();
  return all
    .filter(
      (c) =>
        c.displayName.toLowerCase().includes(q) ||
        c.address.toLowerCase().includes(q),
    )
    .slice(0, 50);
}
