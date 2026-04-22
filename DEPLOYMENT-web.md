# Deployment Guide — Web Stack

Covers production deployment of the Parking Spotter web application:
`frontend-web/` (Next.js) and `backend-web/` (FastAPI). This is distinct
from `DEPLOYMENT.md`, which documents the legacy React Native app and
Flask-on-Render backend.

---

## 1. Architecture at a glance

```
                  parkingspotter.nyc (apex)
                  www.parkingspotter.nyc
                           |
                 [ Cloudflare DNS + CDN ]
                           |
                 [ Cloudflare Pages ]
                 Static export of Next.js
                 /out -> HTML, CSS, JS, images
                           |
       browser JS (NEXT_PUBLIC_WATCHER_API_URL)
                           |
                           v
                  api.parkingspotter.nyc
                           |
                 [ Cloudflare DNS -> Fly.io ]
                           |
                 [ Fly.io Machine (iad/ewr) ]
                 FastAPI + uvicorn on :8080
                 Docker image (python:3.11-slim)
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
  SQLite on Fly       NYC DOT cameras    Resend API
  volume (/data)      webcams.nyctmc.org api.resend.com
                      (image polling)    (outbound SMTP
                                         over HTTPS)
```

Camera frames come from the public NYC DOT camera feed. The FastAPI
service runs an in-process background worker that polls each camera
with at least one active watcher, runs a YOLO model on the frame, and
when the result transitions from "occupied" to "open parking" it sends
an email via Resend.

---

## 2. Vendor summary

| Concern | Vendor | Plan / product | What lives there |
|---|---|---|---|
| Domain registrar | Cloudflare Registrar |Registered with Namecheap | at-cost | `parkingspotter.nyc` |
| Authoritative DNS | Cloudflare DNS | Free | All records for `parkingspotter.nyc` |
| CDN / edge / SSL | Cloudflare | Free | TLS termination, caching, WAF |
| Frontend hosting | Cloudflare Pages | Free | Static export of Next.js (`frontend-web/out`) |
| Backend hosting | Fly.io | Pay-as-you-go (shared-cpu-1x, 2 GB) | FastAPI app, YOLO weights, SQLite |
| Persistent storage | Fly Volumes | Included per-GB | `/data/watchlist.sqlite3` |
| Transactional email | Resend | Free tier / paid | Open-parking alerts from `alerts@parkingspotter.nyc` |
| Ads / conversion | Google Ads (`AW-18107928771`) | — | `gtag.js` loaded site-wide via `app/layout.tsx` |
| Container registry | Fly.io internal registry | Included | Built by `flyctl deploy` |
| Source | GitHub | Free | Monorepo (no CI deploys currently; manual `flyctl` / `wrangler`) |

No other third parties run in production. Google Maps, Firebase, and
the Render-hosted Flask service referenced in `DEPLOYMENT.md` are not
used by the web stack.

---

## 3. DNS configuration (Cloudflare)

Zone: `parkingspotter.nyc`. All records live in the Cloudflare dashboard
under **DNS -> Records**.

### 3.1 Website records

| Type | Name | Content | Proxy | TTL | Purpose |
|---|---|---|---|---|---|
| CNAME | `parkingspotter.nyc` (apex) | `parking-spotter-nyc.pages.dev` | Proxied (orange cloud) | Auto | Points apex to Cloudflare Pages project. Cloudflare performs CNAME flattening on the apex. |
| CNAME | `www` | `parking-spotter-nyc.pages.dev` | Proxied | Auto | `www` variant; also configured as a custom domain inside the Pages project. |

The Pages project name is `parking-spotter-nyc` (see
`frontend-web/package.json` `deploy` script), so the internal hostname
is `parking-spotter-nyc.pages.dev`.

### 3.2 API records

| Type | Name | Content | Proxy | TTL | Purpose |
|---|---|---|---|---|---|
| CNAME | `api` | `parkingspotter-api.fly.dev` | Proxied | Auto | Backend API at `api.parkingspotter.nyc`. App name `parkingspotter-api` comes from `backend-web/fly.toml`. |

Cloudflare's proxy adds a second TLS layer. Fly.io already terminates
TLS on `*.fly.dev`, so the origin connection is `https -> https`. This
works out of the box because Cloudflare's default **SSL/TLS mode** for
proxied custom hostnames is "Full" or "Full (strict)"; anything weaker
will cause redirect loops.

To bind `api.parkingspotter.nyc` to the Fly app the first time:

```
flyctl certs add api.parkingspotter.nyc -a parkingspotter-api
flyctl certs show api.parkingspotter.nyc -a parkingspotter-api
```

Fly will print a validation CNAME or A record to add. If DNS is proxied
through Cloudflare, temporarily set the `api` record to **DNS only**
(grey cloud) until Fly issues the certificate, then re-enable proxy.

### 3.3 Email-authentication records (Resend)

Required on the `parkingspotter.nyc` zone for the sending domain used in
`FROM_EMAIL=alerts@parkingspotter.nyc`. Exact values are supplied by
Resend under **Domains -> parkingspotter.nyc -> DNS records** and must
be copied verbatim.

| Type | Name | Content (example shape) | Proxy | Purpose |
|---|---|---|---|---|
| MX | `send` | `feedback-smtp.us-east-1.amazonses.com` priority 10 | DNS only | SES return-path that Resend uses for bounces. Name is `send.parkingspotter.nyc`. |
| TXT | `send` | `v=spf1 include:amazonses.com ~all` | DNS only | SPF for the `send` subdomain. |
| TXT | `resend._domainkey` | `p=MIGfMA0G...` long public key | DNS only | DKIM public key published by Resend. |
| TXT | `_dmarc` | `v=DMARC1; p=none;` (start permissive, tighten later) | DNS only | DMARC policy for the domain. |

All four must validate in the Resend dashboard before production mail
will deliver without spam-folder risk. TXT records cannot be proxied.

### 3.4 Miscellaneous

- No MX record on the apex is required unless you also want to receive
  mail at `@parkingspotter.nyc`. The outbound-only setup above uses a
  subdomain (`send.parkingspotter.nyc`), which is standard practice.
- There is no wildcard record.

---

## 4. Frontend deployment (Cloudflare Pages)

### 4.1 Stack

- Next.js 16 (App Router), React 19, Tailwind v4.
- `next.config.ts` sets `output: 'export'`, so `next build` emits a
  fully static site into `frontend-web/out/`. There is no Node runtime
  on the hosting side; every route is HTML + JS served from the
  Cloudflare CDN.
- `public/_headers` controls per-path cache / content-type headers
  that Pages honors at the edge.

### 4.2 Environment variables

Stored in **Cloudflare Pages -> Project `parking-spotter-nyc` ->
Settings -> Environment variables (Production)**. `NEXT_PUBLIC_*`
values are baked into the bundle at build time; they are NOT secrets
once deployed.

| Variable | Example | Notes |
|---|---|---|
| `NEXT_PUBLIC_WATCHER_API_URL` | `https://api.parkingspotter.nyc` | Read in `app/lib/watchlist.ts`. |
| `NEXT_PUBLIC_WATCHER_API_KEY` | `<shared key>` | Sent as `X-API-Key` on watch requests. See note 8.2 about its threat model. |

### 4.3 Build and deploy

Local deploy (what the maintainer runs today):

```
cd frontend-web
npm install
npm run deploy
```

That script is:

```
next build && wrangler pages deploy out --project-name parking-spotter-nyc --branch web
```

Prerequisites on the deploy machine:

- `wrangler` installed (`npm i -g wrangler` or the dev-dep in the
  repo), authenticated via `wrangler login`.
- An API token with `Account.Cloudflare Pages: Edit` scope if
  automating from CI.

Cloudflare Pages retains previous deployments indefinitely; rollback is
a one-click operation in the dashboard.

### 4.4 Third-party scripts

The Google Ads global site tag (`AW-18107928771`) is injected on every
route via `next/script` inside `app/layout.tsx` with
`strategy="afterInteractive"`. No separate snippet has to be maintained
per page; the Next.js root layout wraps all routes.

---

## 5. Backend deployment (Fly.io)

### 5.1 Stack

- FastAPI 0.115, uvicorn 0.30, pydantic 2, httpx 0.27.
- Ultralytics YOLO loaded from `models/weights.pt`.
- SQLite in WAL mode, writes serialized through an `asyncio.Lock`.
- Single Docker image; app + worker run in the same process.

### 5.2 Machine configuration

From `backend-web/fly.toml`:

- App: `parkingspotter-api`
- Region: `ewr` (Secaucus / primary).
- VM: `shared-cpu-1x`, 1 vCPU, 2048 MB RAM.
- `internal_port = 8080`, `force_https = true`.
- `auto_stop_machines = "off"`, `min_machines_running = 1`. The worker
  polls every 25 seconds, so autostop is disabled to keep the loop
  alive even with no HTTP traffic.
- Volume `watchlist_data` mounted at `/data`. This is where the
  SQLite file is kept; the repo-committed `backend-web/watchlist.sqlite3`
  is only used for local dev.
- Health check: `GET /health` every 30s.

### 5.3 Secrets

Set once per environment with `flyctl secrets set`. Unlike `[env]`
values in `fly.toml`, secrets are encrypted and are not printed in
deploy output.

| Secret | Source | Used by |
|---|---|---|
| `RESEND_API_KEY` | Resend dashboard -> API Keys | `app/notifier.py` |
| `SHARED_API_KEY` | Generate a long random string | `require_api_key` dependency in `app/main.py`; must match `NEXT_PUBLIC_WATCHER_API_KEY` on the frontend |

Everything else (DB path, weights path, CORS origins, thresholds,
public site URL) is in the public `[env]` block of `fly.toml`.

Example:

```
cd backend-web
flyctl secrets set \
  RESEND_API_KEY=re_xxx \
  SHARED_API_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))') \
  -a parkingspotter-api
```

### 5.4 First-time provisioning

```
cd backend-web

# App + volume
flyctl apps create parkingspotter-api
flyctl volumes create watchlist_data --region ewr --size 1 -a parkingspotter-api

# Secrets (see 5.3)
flyctl secrets set ...

# Custom hostname + TLS
flyctl certs add api.parkingspotter.nyc -a parkingspotter-api

# First deploy
flyctl deploy -a parkingspotter-api
```

`flyctl deploy` builds the image from `backend-web/Dockerfile` on Fly's
remote builder. The Dockerfile installs CPU-only PyTorch from the
`https://download.pytorch.org/whl/cpu` index to avoid pulling the
multi-GB CUDA wheels, then copies `app/`, `models/`, and `scripts/`
into the image. `models/weights.pt` is committed to the repo, so the
YOLO weights ship in the image rather than being downloaded at
startup.

### 5.5 Subsequent deploys

```
cd backend-web
flyctl deploy -a parkingspotter-api
```

To watch logs: `flyctl logs -a parkingspotter-api`.

### 5.6 CORS

`ALLOWED_CORS_ORIGINS` in `fly.toml` currently lists:

- `https://parkingspotter.nyc`
- `https://www.parkingspotter.nyc`
- `http://localhost:3000`

Anything else will be blocked by the FastAPI `CORSMiddleware` in
`app/main.py`. Update `fly.toml` and redeploy when adding a preview
domain.

---

## 6. Email delivery (Resend)

### 6.1 Account-level setup

1. Sign in at `https://resend.com/`.
2. **Domains -> Add Domain -> parkingspotter.nyc**.
3. Publish the four Cloudflare records listed in 3.3 exactly as
   Resend provides them.
4. Wait for all records to show "Verified" in Resend. Until then
   Resend will still accept API calls but deliverability is poor and
   DMARC reports may flag messages.
5. **API Keys -> Create API Key**, sending-domain scope only. Copy the
   resulting `re_...` key straight into
   `flyctl secrets set RESEND_API_KEY=...`.

### 6.2 From address

`FROM_EMAIL=alerts@parkingspotter.nyc`, `FROM_NAME=Parking Spotter`.
The mailbox does not need to exist on an IMAP server; Resend signs the
outbound mail with DKIM for that domain and there is no inbound
delivery. If you later want to receive replies, add a mailbox provider
(e.g. Google Workspace, Fastmail, Migadu) and MX records on the apex.

### 6.3 What gets sent

`app/notifier.py` `send_open_parking_email` POSTs to
`https://api.resend.com/emails` with a JSON payload:

```
{
  "from": "Parking Spotter <alerts@parkingspotter.nyc>",
  "to": ["<watcher email>"],
  "subject": "Parking opened up at <display>",
  "html": "<small HTML body with link to /camera/<address>>",
  "text": "<plain-text equivalent>"
}
```

One email is sent per watcher on each `false -> true` transition of
`open_parking_status`. `notified_on_current_status` is flipped on
success so a long-running "open" state does not cause repeated sends.

### 6.4 Dry-run mode

If `RESEND_API_KEY` is empty the notifier logs
`RESEND_API_KEY not set. Would send email to ... for ...` and returns
`True` without making an HTTP call. This is convenient for local dev
and for staging Fly apps.

---

## 7. Persistent data

- SQLite database at `/data/watchlist.sqlite3` inside the Fly VM.
  Schema lives in `backend-web/app/db.py` (`camera_state`, `watchers`).
- Fly volume `watchlist_data`, 1 GB, region `ewr`. Fly volumes are
  single-host; you cannot scale this app horizontally without moving
  off SQLite.
- No automated backups are configured today. Options:
  - `flyctl ssh console -a parkingspotter-api` then
    `sqlite3 /data/watchlist.sqlite3 '.backup /data/backup.db'` and
    `scp`-equivalent via `flyctl ssh sftp shell`.
  - `flyctl volumes snapshots list watchlist_data` for volume-level
    snapshots (Fly keeps ~5 daily snapshots by default).

If email delivery or inference uptime becomes critical, migrate to
Postgres on Fly (or Neon) so the worker can run on multiple machines.

---

## 8. Secrets and threat model

### 8.1 Secret inventory

| Value | Where it is stored | Where it must never appear |
|---|---|---|
| `RESEND_API_KEY` | Fly secrets only | Git, client bundle, logs |
| `SHARED_API_KEY` | Fly secrets **and** Cloudflare Pages env (as `NEXT_PUBLIC_WATCHER_API_KEY`) | See 8.2 |
| Cloudflare API token | Local `wrangler` credentials | Git |
| Fly API token | `~/.fly/config.yml` | Git |

### 8.2 `NEXT_PUBLIC_WATCHER_API_KEY` is not a secret

Because `frontend-web` is statically exported and the API call is
issued from the browser (`app/lib/watchlist.ts`), any value of
`NEXT_PUBLIC_WATCHER_API_KEY` is visible in the JS bundle served from
Cloudflare Pages. The backend's `X-API-Key` check therefore only
filters out unsophisticated scrapers; it is not authentication.

If that level of abuse protection is not enough, move the API call
behind a server component or a Next.js route handler (which requires
switching `output: 'export'` to a Node / edge runtime, i.e. moving
hosting off Cloudflare Pages static onto Cloudflare Workers or Vercel),
or add Cloudflare Turnstile in front of `/watch` and verify the token
server-side.

### 8.3 Known committed secrets

`backend-web/.env` is checked into the repo and contains a live
`RESEND_API_KEY`. Rotate it in the Resend dashboard, set the new value
via `flyctl secrets set`, and remove the file from tracking
(`git rm --cached backend-web/.env` and add it to `.gitignore`).

---

## 9. End-to-end deploy checklist

First production cutover:

1. Register `parkingspotter.nyc` at Cloudflare Registrar; zone is
   created automatically.
2. Create Cloudflare Pages project `parking-spotter-nyc`, bind custom
   domains `parkingspotter.nyc` and `www.parkingspotter.nyc`, set
   `NEXT_PUBLIC_WATCHER_API_URL` and `NEXT_PUBLIC_WATCHER_API_KEY` env
   vars, then `npm run deploy` from `frontend-web/`.
3. Create Fly app `parkingspotter-api` and `watchlist_data` volume in
   `ewr`. Set `RESEND_API_KEY` and `SHARED_API_KEY` secrets.
   `flyctl deploy`.
4. `flyctl certs add api.parkingspotter.nyc`, add the `api` CNAME in
   Cloudflare per 3.2, wait for green.
5. In Resend, add `parkingspotter.nyc` as a sending domain, publish
   the MX + TXT records from 3.3, wait for "Verified".
6. Smoke test:
   - `curl https://api.parkingspotter.nyc/health` returns
     `{"status":"ok"}`.
   - From the live site, click **Watch** on a camera, submit form,
     confirm `POST /watch` in `flyctl logs`.
   - Force a notification by seeding a watch against a currently-open
     spot (`python backend-web/scripts/seed_watch.py`), confirm an
     email arrives at the target inbox.

Routine redeploy:

- Frontend: `cd frontend-web && npm run deploy`.
- Backend: `cd backend-web && flyctl deploy`.

---

## 10. Monitoring and rollback

- Fly: `flyctl logs -a parkingspotter-api`, `flyctl status`, and the
  `/health` check in `fly.toml` drive restart policy. The dashboard
  shows CPU / memory / volume usage.
- Cloudflare Pages: per-deployment build logs, **Deployments** tab
  supports instant rollback to any prior deploy.
- Resend: **Logs** tab shows every API submission, status, bounces,
  and opens.
- No external uptime monitor is configured. A reasonable addition
  would be UptimeRobot or BetterStack hitting
  `https://api.parkingspotter.nyc/health` on a 1-minute cadence.

Rollback procedure:

- Frontend regression: Cloudflare Pages -> Deployments -> **Rollback**
  on the last known good build.
- Backend regression: `flyctl releases -a parkingspotter-api` to find
  the previous version, then `flyctl deploy --image <digest>` or
  `flyctl deploy` off the previous git commit.
- Data regression: restore from Fly volume snapshot via
  `flyctl volumes snapshots`.

---

## 11. Costs (reference, not a contract)

- Cloudflare DNS + Pages: $0 at current traffic.
- Cloudflare Registrar `.nyc`: around $30/yr at-cost.
- Fly.io: one `shared-cpu-1x` 2 GB machine running 24/7 plus a 1 GB
  volume lands in the low single-digit dollars per month. Outbound
  bandwidth is billed separately but is negligible for 200-byte
  image-check cycles.
- Resend: free tier covers up to 3,000 emails/month and 100/day as of
  writing; paid plans start at $20/month.

---

## 12. Files referenced

- `frontend-web/package.json` — `deploy` script drives Cloudflare Pages.
- `frontend-web/next.config.ts` — `output: 'export'` forces static build.
- `frontend-web/public/_headers` — edge headers served by Pages.
- `frontend-web/app/layout.tsx` — Google Ads `gtag.js` injection.
- `frontend-web/app/lib/watchlist.ts` — client-side call to
  `api.parkingspotter.nyc`.
- `backend-web/fly.toml` — Fly app config, regions, CORS, volume.
- `backend-web/Dockerfile` — CPU-only torch build, runs uvicorn on 8080.
- `backend-web/app/main.py` — FastAPI app, `require_api_key` dependency.
- `backend-web/app/notifier.py` — Resend HTTPS email sender.
- `backend-web/app/worker.py` — DOT image poll + YOLO inference loop.
- `backend-web/app/db.py` — SQLite schema and queries.
