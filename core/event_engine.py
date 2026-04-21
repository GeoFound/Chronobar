"""Event engine implementation for Chronobar platform."""

import queue
import threading
import uuid
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from core.events import EventEnvelope
from core.exceptions import ChronobarError


logger = logging.getLogger(__name__)


EventHandler = Callable[[EventEnvelope], None]


class EventBusError(ChronobarError):
    """Exception raised for event bus errors."""
    pass


class EventBus:
    """Unified event bus implementation."""
    
    def __init__(self, max_queue_size: int = 10000):
        """Initialize event bus.
        
        Args:
            max_queue_size: Maximum queue size for event backlog
        """
        self._queue: queue.Queue[EventEnvelope] = queue.Queue(maxsize=max_queue_size)
        self._handlers: dict[str, list[EventHandler]] = {}
        self._instrument_handlers: dict[tuple[str, str], list[EventHandler]] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        
    def start(self) -> None:
        """Start event bus processing thread."""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._process_events, daemon=True)
        self._thread.start()
        logger.info("Event bus started")
        
    def stop(self) -> None:
        """Stop event bus processing thread."""
        if not self._running:
            return
            
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Event bus stopped")
        
    def put(self, event: EventEnvelope) -> None:
        """Put event into event queue.
        
        Args:
            event: Event to publish
            
        Raises:
            EventBusError: If queue is full
        """
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            raise EventBusError(f"Event queue is full (max size: {self._queue.maxsize})")
            
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to event type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Handler function for events
        """
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            
    def subscribe_instrument(
        self, event_type: str, instrument_id: str, handler: EventHandler
    ) -> None:
        """Subscribe to event type for specific instrument.
        
        Args:
            event_type: Event type to subscribe to
            instrument_id: Instrument ID to filter on
            handler: Handler function for events
        """
        with self._lock:
            key = (event_type, instrument_id)
            if key not in self._instrument_handlers:
                self._instrument_handlers[key] = []
            self._instrument_handlers[key].append(handler)
            
    def _process_events(self) -> None:
        """Process events from queue."""
        while self._running:
            try:
                event = self._queue.get(timeout=1.0)
                self._dispatch_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)
                
    def _dispatch_event(self, event: EventEnvelope) -> None:
        """Dispatch event to registered handlers.
        
        Args:
            event: Event to dispatch
        """
        # Get handlers for event type
        handlers: list[EventHandler] = []
        
        with self._lock:
            # Global handlers for event type
            if event.event_type in self._handlers:
                handlers.extend(self._handlers[event.event_type])
                
            # Instrument-specific handlers
            if event.instrument_id:
                key = (event.event_type, event.instrument_id)
                if key in self._instrument_handlers:
                    handlers.extend(self._instrument_handlers[key])
        
        # Dispatch to handlers with exception isolation
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Handler error for event {event.event_id} "
                    f"(type={event.event_type}): {e}",
                    exc_info=True
                )
