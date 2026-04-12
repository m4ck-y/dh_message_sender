"""
Observability utility for PulseCore.

Provides fire-and-forget async helpers that ship message dispatch events
to the `app_logger_tracer` Observability Gateway via its REST API.

If `SERVICE_LOGGER_TRACER_URL` is not set, the functions silently degrade —
events are only stored in the local InMemoryAuditRepository, ensuring
PulseCore never fails due to a missing observability dependency.
"""
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.config import settings


async def emit_event(
    event: str,
    status: str,
    channel: str,
    recipient: str,
    message_type: str,
    metadata: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> None:
    """
    Emits a structured business event to the Observability Gateway.

    Maps a PulseCore message dispatch outcome to a canonical `EventEntry`
    payload and POSTs it to `POST /v1/events/` on `app_logger_tracer`.

    This call is non-blocking and uses a short timeout (3 s) so that a slow
    or unreachable Gateway never delays the main messaging flow.

    Args:
        event:        Dot-notation event name (e.g. "email.sent", "sms.failed").
        status:       "success" | "failed".
        channel:      Transport channel ("email", "sms", "whatsapp").
        recipient:    Target address (email or phone). PII — keep in metadata only.
        message_type: Template/category key (e.g. "OTP", "Waitlist", "Welcome").
        metadata:     Arbitrary key-value context forwarded as EventEntry.metadata.
        error:        Optional error string on failed dispatches.
    """
    gateway_url = settings.SERVICE_LOGGER_TRACER_URL
    if not gateway_url:
        return  # Graceful degradation — no gateway configured

    payload = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "app_message_sender",
        "session_id": "system",
        "metadata": {
            "channel": channel,
            "message_type": message_type,
            "status": status,
            "recipient": recipient,
            "error": error,
            **(metadata or {}),
        },
    }

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(f"{gateway_url}/v1/events/", json=payload)
    except Exception as exc:
        # Never let a telemetry failure crash the main service
        print(f"[WARN] observability.emit_event failed silently: {exc}")


async def emit_log(
    level: str,
    message: str,
    event: str = "pulsecore.log",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Emits a structured log entry to the Observability Gateway.

    Use this for infrastructure-level messages (startup, config errors, retries)
    that don't map neatly to a business event.

    Args:
        level:   "info" | "warn" | "error" | "debug".
        message: Human-readable description of what happened.
        event:   Dot-notation event key. Defaults to "pulsecore.log".
        metadata:Arbitrary supplemental context.
    """
    gateway_url = settings.SERVICE_LOGGER_TRACER_URL
    if not gateway_url:
        return

    payload = {
        "level": level,
        "event": event,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "app_message_sender",
        "environment": "dev" if settings.DEBUG else "prod",
        "metadata": metadata or {},
    }

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(f"{gateway_url}/v1/logs/", json=payload)
    except Exception as exc:
        print(f"[WARN] observability.emit_log failed silently: {exc}")
