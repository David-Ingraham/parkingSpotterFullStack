from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

from .config import Settings

logger = logging.getLogger(__name__)


def _build_message(
    settings: Settings,
    to_email: str,
    address: str,
    display: str,
) -> EmailMessage:
    site = settings.public_site_url.rstrip("/")
    link = f"{site}/camera/{quote(address, safe='')}"

    msg = EmailMessage()
    msg["From"] = f"{settings.from_name} <{settings.from_email}>"
    msg["To"] = to_email
    msg["Subject"] = f"Parking opened up at {display}"

    body_text = (
        f"A parking spot just opened up at {display}.\n\n"
        f"Live feed: {link}\n\n"
        "This alert was triggered by a computer vision model watching the "
        "NYC DOT camera on your behalf. Image conditions and model accuracy "
        "vary, so confirm visually before driving over."
    )
    msg.set_content(body_text)

    body_html = f"""
      <div style="font-family: system-ui, sans-serif; color: #111;">
        <h2 style="margin: 0 0 12px 0;">Parking opened up at {display}</h2>
        <p>A parking spot just opened up at <strong>{display}</strong>.</p>
        <p><a href="{link}" style="color: #ea580c;">Open the live feed</a></p>
        <p style="font-size: 12px; color: #666;">
          Triggered by a computer vision model watching the NYC DOT camera
          on your behalf. Confirm visually before driving over.
        </p>
      </div>
    """
    msg.add_alternative(body_html, subtype="html")
    return msg


def _send_sync(settings: Settings, message: EmailMessage) -> None:
    if not settings.smtp_host:
        logger.info(
            "SMTP not configured. Would send email to %s with subject %r",
            message["To"],
            message["Subject"],
        )
        return

    if settings.smtp_use_tls:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as s:
            s.starttls()
            if settings.smtp_username:
                s.login(settings.smtp_username, settings.smtp_password)
            s.send_message(message)
    else:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as s:
            if settings.smtp_username:
                s.login(settings.smtp_username, settings.smtp_password)
            s.send_message(message)


async def send_open_parking_email(
    settings: Settings,
    to_email: str,
    address: str,
    display: str,
) -> bool:
    message = _build_message(settings, to_email, address, display)
    try:
        await asyncio.to_thread(_send_sync, settings, message)
        return True
    except Exception as exc:
        logger.exception("Failed to send email to %s: %s", to_email, exc)
        return False
