from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .cameras import get_camera
from .config import Settings, get_settings
from .db import Database
from .inference import OpenParkingDetector
from .schemas import CameraState, WatchCreate, WatchDelete, WatchResponse
from .worker import WatcherWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

MAX_ACTIVE_WATCHES_PER_EMAIL = 5


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    db = Database(settings.resolved_db_path())
    db.initialize()

    detector = OpenParkingDetector(settings)
    detector.load()

    worker = WatcherWorker(settings, db, detector)
    worker.start()

    app.state.settings = settings
    app.state.db = db
    app.state.detector = detector
    app.state.worker = worker

    try:
        yield
    finally:
        await worker.stop()


app = FastAPI(title="Parking Spotter Watchlist", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_cors_origins,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def require_api_key(
    x_api_key: str = Header(default=""),
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.shared_api_key or x_api_key != settings.shared_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def get_db() -> Database:
    return app.state.db


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/watch", response_model=WatchResponse, dependencies=[Depends(require_api_key)])
async def create_watch(
    payload: WatchCreate,
    settings: Settings = Depends(get_settings),
    db: Database = Depends(get_db),
) -> WatchResponse:
    if payload.minutes not in settings.allowed_durations:
        raise HTTPException(
            status_code=400,
            detail=f"minutes must be one of {settings.allowed_durations}",
        )

    camera = get_camera(settings.resolved_cameras_path(), payload.address)
    if camera is None:
        raise HTTPException(status_code=400, detail="Unknown camera address")

    active = await db.count_active_for_email(payload.email)
    if active >= MAX_ACTIVE_WATCHES_PER_EMAIL:
        raise HTTPException(
            status_code=429,
            detail=f"Email already has {active} active watches (max {MAX_ACTIVE_WATCHES_PER_EMAIL})",
        )

    expires_at, count = await db.upsert_watcher(
        address=payload.address,
        camera_id=str(camera["camera_id"]),
        email=payload.email,
        minutes=payload.minutes,
    )

    return WatchResponse(
        status="ok",
        address=payload.address,
        expires_at_utc=expires_at,
        watcher_count=count,
    )


@app.delete("/watch", dependencies=[Depends(require_api_key)])
async def delete_watch(
    payload: WatchDelete,
    db: Database = Depends(get_db),
) -> dict:
    deleted = await db.delete_watcher(payload.address, payload.email)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="No matching watch found")
    return {"status": "ok", "deleted": deleted}


@app.get("/state/{address}", response_model=CameraState, dependencies=[Depends(require_api_key)])
async def get_camera_state(
    address: str,
    db: Database = Depends(get_db),
) -> CameraState:
    row = await db.get_state(address)
    if row is None:
        return CameraState(
            address=address,
            open_parking_status=None,
            last_checked_utc=None,
            watcher_count=0,
        )
    raw = row["open_parking_status"]
    return CameraState(
        address=row["address"],
        open_parking_status=None if raw is None else bool(raw),
        last_checked_utc=row["last_checked_utc"],
        watcher_count=int(row["watcher_count"]),
    )
