import { getAllCameras, haversineMiles, type Camera } from "./cameras";

export type Neighborhood = {
  slug: string;
  name: string;
  borough: string;
  latitude: number;
  longitude: number;
  radiusMiles: number;
  intro: string;
  tips: string[];
};

export const NEIGHBORHOODS: readonly Neighborhood[] = [
  {
    slug: "soho",
    name: "SoHo",
    borough: "Manhattan",
    latitude: 40.7233,
    longitude: -74.003,
    radiusMiles: 0.5,
    intro:
      "SoHo's cast-iron side streets fill up by late morning on weekdays and stay packed through the evening. The numbered cross streets and cobblestone blocks like Mercer, Greene, Wooster, and Crosby hold the best odds for a free spot, but they enforce alternate-side cleaning twice a week and sign-reading is unforgiving. Broadway, Lafayette, and West Broadway are metered through most of the day. The live cameras below cover the busiest SoHo approaches, so you can see whether a block is already lined solid before committing to a detour.",
    tips: [
      "Numbered cross streets (Prince, Spring, Broome, Grand) are more likely to have free parking than the north-south avenues.",
      "Alternate-side street cleaning runs twice a week on most blocks; check posted signs.",
      "Weekend tourist traffic peaks Saturday afternoon. Early mornings (before 9am) and late evenings (after 8pm) give the best odds.",
      "Commercial loading zones on Broadway are enforced 7am–7pm weekdays — read the sign even if a spot looks open.",
    ],
  },
  {
    slug: "east-village",
    name: "East Village",
    borough: "Manhattan",
    latitude: 40.7265,
    longitude: -73.9815,
    radiusMiles: 0.55,
    intro:
      "The East Village grid of Avenues A through D and the numbered streets between Houston and 14th is one of the densest residential-parking zones in Manhattan. Supply collapses after 7pm on weeknights when the bar and restaurant crowd arrives, and stays thin through Sunday evening. Tompkins Square Park acts as the gravitational center — blocks adjacent to it turn over least often. Cameras along 1st Ave, 2nd Ave, and 14th St let you gauge traffic flow before detouring into the grid.",
    tips: [
      "Parking is noticeably easier east of Avenue B than west of it; most visitor traffic stops at Avenue A.",
      "Friday and Saturday nights are the hardest; Sunday mornings free up as weekend visitors leave.",
      "Bike lanes on 1st and 2nd Avenues are camera-enforced. Do not stop in them even briefly.",
      "14th St has 24/7 busway restrictions for most of its length — private vehicles cannot stop.",
    ],
  },
  {
    slug: "lower-east-side",
    name: "Lower East Side",
    borough: "Manhattan",
    latitude: 40.718,
    longitude: -73.9857,
    radiusMiles: 0.45,
    intro:
      "The Lower East Side has short blocks, heavy restaurant and nightlife turnover, and the Williamsburg Bridge approach funneling traffic through Delancey St. Orchard, Ludlow, and Rivington fill up fastest. Side streets below Delancey (Broome, Grand, Hester) offer better odds on weekday mornings before commuters arrive. Weekend nights are nearly impossible without circling. Use the cameras to check Delancey and Houston traffic before committing to an approach.",
    tips: [
      "Delancey St is a primary feeder to the Williamsburg Bridge; avoid stopping on it during rush hours.",
      "Overnight Saturday–Sunday is peak demand from nightlife. Before 8pm or after 3am is more realistic.",
      "Blocks near the bridge ramps (Clinton, Suffolk) turn over more than blocks near Seward Park.",
    ],
  },
  {
    slug: "west-village",
    name: "West Village",
    borough: "Manhattan",
    latitude: 40.7358,
    longitude: -74.0036,
    radiusMiles: 0.5,
    intro:
      "The West Village has one of the most difficult parking environments in the city. The street grid abandons the Manhattan rectangle — Bleecker, Bedford, Christopher, and Commerce all bend and intersect at odd angles, and block lengths are short. Garages are expensive and sparse. Residents compete with tourist and nightlife traffic, and the West Side Highway on the west edge doesn't provide relief parking. Cameras along Hudson St, 7th Ave South, and Greenwich Ave give the best picture of conditions.",
    tips: [
      "Hudson St and 7th Ave South carry most through-traffic; side streets like Bank, Perry, and Charles are quieter but short.",
      "Evenings near Sheridan Square and Christopher St are the hardest, especially Thursday–Saturday.",
      "The meters on 6th Ave run later than most Manhattan meters.",
    ],
  },
  {
    slug: "chelsea",
    name: "Chelsea",
    borough: "Manhattan",
    latitude: 40.7465,
    longitude: -74.0014,
    radiusMiles: 0.55,
    intro:
      "Chelsea runs from roughly 14th to 30th St between 6th Ave and the West Side Highway. The High Line, Hudson Yards, and Chelsea Market pull steady visitor traffic, and the gallery and nightlife scenes layer on top. Streets in the low 20s west of 8th Ave are heavily metered and actively enforced. The best free-parking odds are on 10th and 11th Avenues above 24th St, and on the side streets east of 8th. Cameras along 10th Ave, 11th Ave, and West 34th St cover the main approaches.",
    tips: [
      "Hudson Yards events spike demand on 10th and 11th Ave. Check event schedules before planning.",
      "The Lincoln Tunnel approach on 9th Ave in the 30s creates congestion weekday afternoons.",
      "Street cleaning on avenues here is typically Monday/Thursday or Tuesday/Friday cycles.",
    ],
  },
  {
    slug: "midtown",
    name: "Midtown",
    borough: "Manhattan",
    latitude: 40.7549,
    longitude: -73.984,
    radiusMiles: 0.75,
    intro:
      "Midtown is almost entirely metered or no-standing during the business day. Between 34th and 59th St, expect commercial-zone restrictions, active enforcement, and tow-zone stretches around Penn Station, the Port Authority, Bryant Park, and Grand Central. Street parking exists but is thin and tightly regulated. Evenings and weekends open up some residential-side pockets in the 50s east of 3rd Ave and west of 9th Ave. The cameras let you judge traffic volume — useful both for finding a spot and for deciding whether to approach at all.",
    tips: [
      "Before 7pm on weekdays, plan on a garage unless you have a specific short-term metered spot in mind.",
      "After 7pm, the east 50s (between 2nd and 3rd Ave) and the west 50s (between 9th and 10th) are the most realistic free-parking zones.",
      "No-standing zones around theaters, hotels, and consulates are enforced 24/7. Always read the sign.",
    ],
  },
  {
    slug: "upper-east-side",
    name: "Upper East Side",
    borough: "Manhattan",
    latitude: 40.7736,
    longitude: -73.9566,
    radiusMiles: 0.85,
    intro:
      "The Upper East Side has the cleanest street grid in the city and predictable parking patterns, which cuts both ways — the rules are simple, but so is the competition for spots. Park Ave, Madison, and 5th Ave carry heavy traffic; side streets in the East 70s–90s are the usable parking. Proximity to Central Park, the museums, and major hospitals keeps demand steady through the day. Alternate-side cycles are strictly enforced. Cameras along 1st, 2nd, and 3rd Ave give a good read on flow.",
    tips: [
      "East of Lexington is generally easier than west of it.",
      "Museum Mile on 5th Ave has permanent no-standing zones along the park side.",
      "Evenings near NY-Presbyterian / Weill Cornell (York Ave in the 60s–70s) are tight; patient family visits dominate demand.",
    ],
  },
  {
    slug: "upper-west-side",
    name: "Upper West Side",
    borough: "Manhattan",
    latitude: 40.787,
    longitude: -73.9754,
    radiusMiles: 0.85,
    intro:
      "The Upper West Side runs from Columbus Circle to about 110th St between Central Park West and the Hudson. Side streets between Columbus and Amsterdam are densely residential and turn over slowly. Riverside Drive and West End Ave are somewhat easier but still tight during alt-side suspension days. Lincoln Center, the Natural History Museum, and Columbia traffic push demand. The cameras along Broadway, West End, and the numbered cross streets cover the main north-south approaches.",
    tips: [
      "West End Ave and Riverside Dr are usually the easiest avenues.",
      "Alternate-side suspension days (see NYC DOT calendar) are the worst parking days — everyone stays put.",
      "Columbia and Barnard area (110s-120s) is its own micro-market; student move-in weeks are unworkable.",
    ],
  },
  {
    slug: "harlem",
    name: "Harlem",
    borough: "Manhattan",
    latitude: 40.8116,
    longitude: -73.9465,
    radiusMiles: 1.0,
    intro:
      "Harlem's wide avenues — Lenox (Malcolm X Blvd), Frederick Douglass (8th Ave), Adam Clayton Powell (7th Ave), and 125th St — make it easier to park than anywhere south of 96th St. Side streets in the 120s and 130s have long blocks and turn over through the day. Weekends around Marcus Garvey Park and 125th St commercial district are busier. The cameras cover the main east-west crosstown approaches and the avenues.",
    tips: [
      "125th St itself is commercial and heavily regulated. Park on the cross streets, not on 125th.",
      "Alternate-side cycles here are straightforward; most blocks are Monday-Thursday or Tuesday-Friday.",
      "Sunday mornings see church traffic around major congregations — check surroundings before settling in.",
    ],
  },
  {
    slug: "williamsburg",
    name: "Williamsburg",
    borough: "Brooklyn",
    latitude: 40.7081,
    longitude: -73.9571,
    radiusMiles: 0.8,
    intro:
      "Williamsburg's parking got markedly harder after the L-train redevelopment wave. Bedford Ave, Metropolitan, Grand St, and Havemeyer are the main arteries; side streets like Berry, Wythe, and Roebling carry the residential demand. The Brooklyn-Queens Expressway cuts through the neighborhood and eats curb on the blocks adjacent to it. North of Grand is visitor-heavy with bars, restaurants, and waterfront; south of Grand (South Williamsburg) is primarily residential with strict alt-side. Cameras on the bridge approach and on Wythe Ave cover the busiest approaches.",
    tips: [
      "South Williamsburg (below Grand) typically has better free-parking odds than north Williamsburg.",
      "Friday and Saturday evenings are the hardest. Sunday afternoons are tolerable.",
      "Do not park near the Williamsburg Bridge approach on weekdays — enforcement is active.",
    ],
  },
  {
    slug: "park-slope",
    name: "Park Slope",
    borough: "Brooklyn",
    latitude: 40.671,
    longitude: -73.9814,
    radiusMiles: 0.75,
    intro:
      "Park Slope's brownstone blocks between 4th Ave and Prospect Park West are dominated by long-term residents with stable alternate-side routines. 5th Ave and 7th Ave are the commercial spines and carry most through-traffic. The numbered streets in the low 10s (around Grand Army Plaza) are easiest; deeper into the Slope (Carroll, Garfield, 1st–3rd Streets) turnover slows. Prospect Park events and farmer's market days spike demand. Cameras on Flatbush Ave and around Grand Army Plaza read the neighborhood's traffic well.",
    tips: [
      "4th Ave is generally the easiest north-south option but has heavy truck and bus traffic.",
      "Saturday mornings at Grand Army Plaza farmer's market are the hardest.",
      "Alt-side in Park Slope is strictly enforced; do not assume generous grace windows.",
    ],
  },
  {
    slug: "astoria",
    name: "Astoria",
    borough: "Queens",
    latitude: 40.7644,
    longitude: -73.9235,
    radiusMiles: 0.9,
    intro:
      "Astoria is one of the most realistic Queens neighborhoods for street parking. Block lengths are longer than Manhattan, the grid is consistent, and the residential density is moderate. Ditmars Blvd, Steinway St, 30th Ave, and Broadway are the main retail corridors and carry the heaviest demand. Side streets in the 20s through 40s generally have space, though alt-side cycles are strict. The cameras cover the main BQE and Grand Central Parkway approaches and the crosstown avenues.",
    tips: [
      "Side streets even a block off Steinway or 30th Ave open up dramatically.",
      "BQE-adjacent blocks have long-term signage restrictions — read carefully.",
      "Metered strips on Ditmars and 30th Ave run into the evening.",
    ],
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
