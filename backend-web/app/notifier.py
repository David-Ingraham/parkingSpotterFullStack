from __future__ import annotations

import logging
from urllib.parse import quote

import httpx

from .config import Settings

logger = logging.getLogger(__name__)


def _build_payload(
    settings: Settings,
    to_email: str,
    address: str,
    display: str,
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

    html = (
        '<div style="font-family: system-ui, sans-serif; color: #111;">'
        f'<h2 style="margin: 0 0 12px 0;">Parking opened up at {display}</h2>'
        f'<p>A parking spot just opened up at <strong>{display}</strong>.</p>'
        f'<p><a href="{link}" style="color: #ea580c;">Open the live feed</a></p>'
        '<p style="font-size: 12px; color: #666;">'
        'Triggered by a computer vision model watching the NYC DOT camera '
        'on your behalf. Confirm visually before driving over.'
        '</p>'
        '</div>'
    )

    return {
        "from": f"{settings.from_name} <{settings.from_email}>",
        "to": [to_email],
        "subject": subject,
        "html": html,
        "text": text,
    }


async def send_open_parking_email(
    settings: Settings,
    to_email: str,
    address: str,
    display: str,
) -> bool:
    if not settings.resend_api_key:
        logger.info(
            "RESEND_API_KEY not set. Would send email to %s for %s",
            to_email,
            display,
        )
        return True

    payload = _build_payload(settings, to_email, address, display)
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
            "Resend accepted email id=%s to=%s address=%s",
            message_id,
            to_email,
            address,
        )
        return True

    logger.error(
        "Resend rejected email to %s: HTTP %d body=%s",
        to_email,
        resp.status_code,
        resp.text[:500],
    )
    return False
