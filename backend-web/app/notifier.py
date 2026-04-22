from __future__ import annotations

import base64
import logging
from typing import Optional
from urllib.parse import quote

import httpx

from .config import Settings

logger = logging.getLogger(__name__)


_INLINE_IMAGE_CID = "parking-frame"


def _build_payload(
    settings: Settings,
    to_email: str,
    address: str,
    display: str,
    image_bytes: Optional[bytes] = None,
    image_filename: str = "parking.jpg",
) -> dict:
    site = settings.public_site_url.rstrip("/")
    link = f"{site}/camera/{quote(address, safe='')}"
    subject = f"Parking opened up at {display}"

    text = (
        f"A parking spot just opened up at {display}.\n\n"
        f"Live feed: {link}\n\n"
        "This alert was triggered by a computer vision model watching the "
        "NYC DOT camera on your behalf. Image conditions and model accuracy "
        "vary, so confirm visually before driving over."
    )

    image_block = ""
    if image_bytes is not None:
        image_block = (
            f'<p><img src="cid:{_INLINE_IMAGE_CID}" alt="Detected open parking at {display}" '
            'style="max-width:100%; border-radius:8px;"></p>'
        )

    html = (
        '<div style="font-family: system-ui, sans-serif; color: #111;">'
        f'<h2 style="margin: 0 0 12px 0;">Parking opened up at {display}</h2>'
        f'<p>A parking spot just opened up at <strong>{display}</strong>.</p>'
        f'{image_block}'
        f'<p><a href="{link}" style="color: #ea580c;">Open the live feed</a></p>'
        '<p style="font-size: 12px; color: #666;">'
        'Triggered by a computer vision model watching the NYC DOT camera '
        'on your behalf. Confirm visually before driving over.'
        '</p>'
        '</div>'
    )

    payload: dict = {
        "from": f"{settings.from_name} <{settings.from_email}>",
        "to": [to_email],
        "subject": subject,
        "html": html,
        "text": text,
    }

    if image_bytes is not None:
        payload["attachments"] = [
            {
                "filename": image_filename,
                "content": base64.b64encode(image_bytes).decode("ascii"),
                "content_type": "image/jpeg",
                "content_id": _INLINE_IMAGE_CID,
            }
        ]

    return payload


async def send_open_parking_email(
    settings: Settings,
    to_email: str,
    address: str,
    display: str,
    image_bytes: Optional[bytes] = None,
    image_filename: str = "parking.jpg",
) -> bool:
    if not settings.resend_api_key:
        logger.info(
            "RESEND_API_KEY not set. Would send email to %s for %s (attachment_bytes=%s)",
            to_email,
            display,
            len(image_bytes) if image_bytes is not None else 0,
        )
        return True

    payload = _build_payload(
        settings,
        to_email,
        address,
        display,
        image_bytes=image_bytes,
        image_filename=image_filename,
    )
    url = f"{settings.resend_api_base.rstrip('/')}/emails"
    headers = {
        "Authorization": f"Bearer {settings.resend_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.resend_request_timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        logger.exception("HTTP error posting to Resend for %s: %s", to_email, exc)
        return False

    if resp.status_code in (200, 201):
        try:
            data = resp.json()
            message_id = data.get("id")
        except ValueError:
            message_id = None
        logger.info(
            "Resend accepted email id=%s to=%s address=%s attachment_bytes=%d",
            message_id,
            to_email,
            address,
            len(image_bytes) if image_bytes is not None else 0,
        )
        return True

    logger.error(
        "Resend rejected email to %s: HTTP %d body=%s",
        to_email,
        resp.status_code,
        resp.text[:500],
    )
    return False
