import type { MetadataRoute } from "next";
import { getAllCameras } from "./lib/cameras";
import { getNeighborhoodsWithCameras } from "./lib/neighborhoods";

export const dynamic = "force-static";

const SITE_URL = "https://parkingspotter.nyc";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: `${SITE_URL}/`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${SITE_URL}/parking`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.9,
    },
    {
      url: `${SITE_URL}/browse`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.7,
    },
    {
      url: `${SITE_URL}/nearest`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.5,
    },
  ];

  const neighborhoodRoutes: MetadataRoute.Sitemap = getNeighborhoodsWithCameras()
    .map((n) => ({
      url: `${SITE_URL}/parking/${n.slug}`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.8,
    }));

  const cameraRoutes: MetadataRoute.Sitemap = getAllCameras().map((camera) => ({
    url: `${SITE_URL}/camera/${encodeURIComponent(camera.address)}`,
    lastModified: now,
    changeFrequency: "monthly",
    priority: 0.6,
  }));

  return [...staticRoutes, ...neighborhoodRoutes, ...cameraRoutes];
}
