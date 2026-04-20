import { ImageResponse } from "next/og";

export const dynamic = "force-static";

export const alt = "Parking Spotter NYC — Live street cameras for NYC parking";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px",
          background:
            "linear-gradient(135deg, #0a0a0a 0%, #18181b 60%, #1c1917 100%)",
          color: "#f4f4f5",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "20px",
              height: "20px",
              borderRadius: "9999px",
              background: "#f97316",
            }}
          />
          <div
            style={{
              fontSize: 28,
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              color: "#fdba74",
              fontWeight: 700,
            }}
          >
            Parking Spotter NYC
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div
            style={{
              fontSize: 88,
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
              color: "#fafafa",
            }}
          >
            Find street parking in NYC.
          </div>
          <div
            style={{
              fontSize: 36,
              color: "#a1a1aa",
              lineHeight: 1.3,
              maxWidth: "900px",
            }}
          >
            Live NYC DOT traffic cameras for the streets with the most
            sought-after parking.
          </div>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: 24,
            color: "#71717a",
          }}
        >
          <div style={{ display: "flex" }}>parkingspotter.nyc</div>
          <div style={{ display: "flex" }}>No signup. No app install.</div>
        </div>
      </div>
    ),
    { ...size },
  );
}
