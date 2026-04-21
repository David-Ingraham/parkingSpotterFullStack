# backend-web

Watchlist service for the Parking Spotter web frontend. Runs a FastAPI app
with a single-process async worker that polls NYC DOT camera feeds, runs a
YOLO model against frames, and sends email alerts when a watched spot goes
from "no parking" to "parking open."

## Layout

```
backend-web/
  app/
    main.py         FastAPI app and routes
    config.py       Env-backed settings
    db.py           SQLite schema and queries
    schemas.py      Pydantic request/response models
    cameras.py      Reads camera metadata from frontend-web/app/data/cameras.json
    inference.py    YOLO wrapper (ultralytics)
    notifier.py     Resend HTTPS API email sender
    worker.py       Poll loop (fetch image, infer, diff status, notify)
  requirements.txt
  .env.example
```

## Setup

```
cd backend-web
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

- `WEIGHTS_PATH` points to `weights.pt` (defaults to the repo root).
- `CAMERAS_JSON_PATH` points to the frontend cameras file.
- `OPEN_CLASSES` is the set of YOLO class names that indicate an open spot.
  Adjust to match the labels the model was trained on.
- `RESEND_API_KEY` and `FROM_EMAIL` control email delivery via the Resend
  HTTPS API. Leaving `RESEND_API_KEY` empty makes the notifier log messages
  instead of sending them, which is fine for local dev. `FROM_EMAIL` must
  use a domain that is verified in your Resend account.
- `SHARED_API_KEY` must match the key the Next.js proxy sends in
  `X-API-Key`.

## Run

```
uvicorn app.main:app --reload --port 8080
```

## Endpoints

All endpoints except `/health` require header `X-API-Key: <SHARED_API_KEY>`.

- `GET /health`
- `POST /watch` body `{"address": "Grand_St_Bowery", "email": "a@b.com", "minutes": 30}`
- `DELETE /watch` body `{"address": "Grand_St_Bowery", "email": "a@b.com"}`
- `GET /state/{address}`

## Testing

Three scripts cover the three things most likely to be wrong. Run them
from `backend-web/` with the venv activated.

### 1. Confirm the YOLO class names

```
python scripts/inspect_model.py
```

Prints the class-index -> label map baked into `weights.pt` and flags any
label in `OPEN_CLASSES` / `OCCUPIED_CLASSES` that isn't present in the
model. Expected output for the current weights:

```
0: open_parking
1: parked_cars
```

If those strings differ, update `.env` and re-run.

### 2. Run inference on a live camera frame

```
python scripts/test_camera.py Grand_St_Bowery --save /tmp/frame.jpg
```

Fetches one image from NYC DOT, runs the detector, prints True / False /
None. Save-to-disk is optional — useful if you want to sanity check what
the model saw.

### 3. Smoke test the HTTP API

In one terminal:

```
uvicorn app.main:app --reload --port 8080
```

In another:

```
curl http://localhost:8080/health

python scripts/seed_watch.py Grand_St_Bowery you@example.com 30
```

`seed_watch.py` submits a watch and then reads `/state/<address>`. With
`RESEND_API_KEY` empty you'll see "Would send email" lines in the uvicorn
log when the worker detects an open-parking transition.

### 4. Frontend

```
cd ../frontend-web
cp .env.example .env.local   # then edit
npm run dev
```

Open `http://localhost:3000`, click Watch on any camera card, submit the
form. Check the backend log for the `POST /watch` line and the SQLite
file (`sqlite3 watchlist.sqlite3 'select * from watchers'`) to confirm
the row landed.

## Notes

- The worker serializes all SQLite writes through an asyncio lock. SQLite
  is opened in WAL mode for concurrent readers.
- Inference runs in a thread via `asyncio.to_thread` so it does not block
  the event loop.
- An email is sent only on the false -> true edge of `open_parking_status`.
  Each watcher gets at most one email per status change; the flag resets
  when the status flips.
- Per-email active watch cap is hardcoded at 5 in `main.py`. Adjust if
  needed.
