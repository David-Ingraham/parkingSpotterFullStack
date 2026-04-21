import { getAllCameras, haversineMiles, type Camera } from "./cameras";

export type Neighborhood = {
  slug: string;
  name: string;
  borough: string;
  latitude: number;
  longitude: number;
  radiusMiles: number;
};

export const NEIGHBORHOODS: readonly Neighborhood[] = [
  {
    slug: "soho",
    name: "SoHo",
    borough: "Manhattan",
    latitude: 40.7233,
    longitude: -74.003,
    radiusMiles: 0.5,
  },
  {
    slug: "east-village",
    name: "East Village",
    borough: "Manhattan",
    latitude: 40.7265,
    longitude: -73.9815,
    radiusMiles: 0.55,
  },
  {
    slug: "lower-east-side",
    name: "Lower East Side",
    borough: "Manhattan",
    latitude: 40.718,
    longitude: -73.9857,
    radiusMiles: 0.45,
  },
  {
    slug: "west-village",
    name: "West Village",
    borough: "Manhattan",
    latitude: 40.7358,
    longitude: -74.0036,
    radiusMiles: 0.5,
  },
  {
    slug: "chelsea",
    name: "Chelsea",
    borough: "Manhattan",
    latitude: 40.7465,
    longitude: -74.0014,
    radiusMiles: 0.55,
  },
  {
    slug: "midtown",
    name: "Midtown",
    borough: "Manhattan",
    latitude: 40.7549,
    longitude: -73.984,
    radiusMiles: 0.75,
  },
  {
    slug: "upper-east-side",
    name: "Upper East Side",
    borough: "Manhattan",
    latitude: 40.7736,
    longitude: -73.9566,
    radiusMiles: 0.85,
  },
  {
    slug: "upper-west-side",
    name: "Upper West Side",
    borough: "Manhattan",
    latitude: 40.787,
    longitude: -73.9754,
    radiusMiles: 0.85,
  },
  {
    slug: "harlem",
    name: "Harlem",
    borough: "Manhattan",
    latitude: 40.8116,
    longitude: -73.9465,
    radiusMiles: 1.0,
  },
  {
    slug: "williamsburg",
    name: "Williamsburg",
    borough: "Brooklyn",
    latitude: 40.7081,
    longitude: -73.9571,
    radiusMiles: 0.8,
  },
  {
    slug: "park-slope",
    name: "Park Slope",
    borough: "Brooklyn",
    latitude: 40.671,
    longitude: -73.9814,
    radiusMiles: 0.75,
  },
  {
    slug: "astoria",
    name: "Astoria",
    borough: "Queens",
    latitude: 40.7644,
    longitude: -73.9235,
    radiusMiles: 0.9,
  },
] as const;

export function getNeighborhoodForCamera(camera: Camera): Neighborhood | null {
  let best: { n: Neighborhood; d: number } | null = null;
  for (const n of NEIGHBORHOODS) {
    const d = haversineMiles(camera.latitude, camera.longitude, n.latitude, n.longitude);
    if (d <= n.radiusMiles && (!best || d < best.d)) {
      best = { n, d };
    }
  }
  return best?.n ?? null;
}

export function getCamerasInNeighborhood(slug: string): Camera[] {
  const target = getNeighborhood(slug);
  if (!target) return [];
  return getAllCameras()
    .map((c) => ({
      c,
      d: haversineMiles(c.latitude, c.longitude, target.latitude, target.longitude),
      n: getNeighborhoodForCamera(c),
    }))
    .filter((x) => x.n?.slug === slug)
    .sort((a, b) => a.d - b.d)
    .map((x) => x.c);
}

export function getNeighborhood(slug: string): Neighborhood | null {
  return NEIGHBORHOODS.find((n) => n.slug === slug) ?? null;
}

export function getNeighborhoodsWithCameras(): Array<
  Neighborhood & { cameraCount: number }
> {
  return NEIGHBORHOODS.map((n) => ({
    ...n,
    cameraCount: getCamerasInNeighborhood(n.slug).length,
  })).filter((n) => n.cameraCount > 0);
}
