from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class WatchCreate(BaseModel):
    address: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    minutes: int


class WatchDelete(BaseModel):
    address: str = Field(..., min_length=1, max_length=200)
    email: EmailStr


class WatchResponse(BaseModel):
    status: str
    address: str
    expires_at_utc: str
    watcher_count: int


class CameraState(BaseModel):
    address: str
    open_parking_status: Optional[bool]
    last_checked_utc: Optional[str]
    watcher_count: int
