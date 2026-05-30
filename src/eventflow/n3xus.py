"""Bridge: EventFlow event creation → n3xusDB event_outbox."""

import logging

from n3xuslib import N3xusClient
from n3xuslib.config import N3xusConfig

logger = logging.getLogger("eventflow.n3xus")


async def emit_event(
    *,
    event_type: str,
    severity: str = "info",
    title: str,
    payload: dict | None = None,
    tags: list[str] | None = None,
) -> str | None:
    config = N3xusConfig.from_env()

    try:
        async with N3xusClient(config) as client:
            return await client.emit(
                source="eventflow",
                source_instance=config.source_instance,
                event_type=event_type,
                severity=severity,
                title=title,
                payload=payload or {},
                tags=tags or ["eventflow"],
            )
    except Exception as e:
        logger.debug("n3xuslib emit failed: %s", e)
        return None
