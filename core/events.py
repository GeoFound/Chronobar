"""Core event model for Chronobar platform."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class EventEnvelope:
    """Event envelope for unified event bus."""
    event_id: str
    event_type: str
    source: str
    ts: datetime
    instrument_id: str | None = None
    session_id: str | None = None
    payload: Any = None
    trace_id: str = ""
    replayable: bool = True
    version: str = "1.2"
